use std::any::Any;
use std::fs::File;
use std::io;
use std::io::{BufWriter, ErrorKind, Read, Write};
use std::mem::MaybeUninit;
use std::ops::{Deref, DerefMut};
use std::time::Duration;
use anyhow::{bail, Result};
use bytes::{Buf, BufMut, Bytes, BytesMut};
use nom::{Err, IResult};
use nom::error::Error;
use nom::Needed::Unknown;
use reqwest::blocking::Response;
use reqwest::header::{ACCEPT, ACCEPT_ENCODING, ACCEPT_LANGUAGE, HeaderMap, USER_AGENT};
use tracing::{info, warn};
use crate::downloader::Segment;
use crate::flv_parser::{aac_audio_packet_header, AACPacketType, avc_video_packet_header, AVCPacketType, CodecId, complete_tag, FrameType, header, script_data, SoundFormat, tag_data, tag_header, TagData, TagHeader, TagType};
use crate::flv_writer;
use crate::flv_writer::{create_flv_file, FlvTag, TagDataHeader, write_previous_tag_size, write_tag_header};
use byteorder::{BigEndian, ReadBytesExt};
use std::io::Cursor;

pub fn download(mut connection: Connection, file_name: &str, segment: Segment) ->Result<()> {
    match parse_flv(connection, file_name, segment) {
        Ok(_) => {
            info!("Done... {file_name}");
        }
        Err(e) => {
            warn!("{e}")
        }
    }
    Ok(())
}


fn parse_flv(mut connection: Connection, file_name: &str, segment: Segment) -> core::result::Result<(), crate::error::Error> {
    let mut flv_tags_cache: Vec<(TagHeader, Bytes, Bytes)> = Vec::new();

    let previous_tag_size = connection.read_frame(4)?;
    // let mut rdr = Cursor::new(previous_tag_size);
    // println!("{}", rdr.read_u32::<BigEndian>().unwrap());
    // let file = std::fs::File::create(format!("{file_name}_flv.json"))?;
    // let mut writer = BufWriter::new(file);
    // flv_writer::to_json(&mut writer, &header)?;

    let mut out = create_flv_file(file_name)?;
    let mut first_tag_time = 0;
    let mut downloaded_size = 9 + 4;
    let mut file_index: u32 = 0;
    let mut on_meta_data = None;
    let mut aac_sequence_header = None;
    let mut h264_sequence_header = None;
    let mut prev_timestamp = 0;
    loop {
        let tag_header_bytes = connection.read_frame(11)?;
        if tag_header_bytes.is_empty() {
            // let mut rdr = Cursor::new(tag_header_bytes);
            // println!("{}", rdr.read_u32::<BigEndian>().unwrap());
            break;
        }

        let (_, mut tag_header) = map_parse_err(tag_header(&tag_header_bytes), "tag header")?;
        // write_tag_header(&mut out, &tag_header)?;

        let bytes = connection.read_frame(tag_header.data_size as usize)?;
        let previous_tag_size = connection.read_frame(4)?;
        // out.write(&bytes)?;
        let (i, flv_tag_data) = map_parse_err(tag_data(tag_header.tag_type, tag_header.data_size as usize)(&bytes), "tag data")?;
        let flv_tag = match flv_tag_data {
            TagData::Audio(audio_data) => {
                let packet_type = if audio_data.sound_format == SoundFormat::AAC {
                    let (_, packet_header) = aac_audio_packet_header(audio_data.sound_data).expect("Error in parsing aac audio packet header.");
                    if packet_header.packet_type == AACPacketType::SequenceHeader {
                        if aac_sequence_header.is_some() {
                            warn!("Unexpected aac sequence header tag. {tag_header:?}");
                            // panic!("Unexpected aac_sequence_header tag.");
                        }
                        aac_sequence_header = Some((tag_header, bytes.clone(), previous_tag_size.clone()))
                    }
                    Some(packet_header.packet_type)
                } else { None };
                let flv_tag = FlvTag {
                    header: tag_header,
                    data: TagDataHeader::Audio{
                        sound_format: audio_data.sound_format,
                        sound_rate: audio_data.sound_rate,
                        sound_size: audio_data.sound_size,
                        sound_type: audio_data.sound_type,
                        packet_type
                    }
                };
                flv_tag
            }
            TagData::Video(video_data) => {
                let (packet_type, composition_time) = if CodecId::H264 == video_data.codec_id {
                    let (_, avc_video_header) = avc_video_packet_header(video_data.video_data).expect("Error in parsing avc video packet header.");
                    if avc_video_header.packet_type == AVCPacketType::SequenceHeader {
                        if h264_sequence_header.is_some() {
                            warn!("Unexpected h264 sequence header tag. {tag_header:?}");
                            // panic!("Unexpected h264 sequence header tag.");
                        }
                        h264_sequence_header = Some((tag_header, bytes.clone(), previous_tag_size.clone()));
                    }
                    (Some(avc_video_header.packet_type), Some(avc_video_header.composition_time))
                } else { (None, None) };
                let flv_tag = FlvTag {
                    header: tag_header,
                    data: TagDataHeader::Video {
                        frame_type: video_data.frame_type,
                        codec_id: video_data.codec_id,
                        packet_type,
                        composition_time,
                    }
                };
                flv_tag
            }
            TagData::Script => {
                let (_, tag_data) = script_data(i).expect("Error in parsing script tag.");
                if on_meta_data.is_some() {
                    warn!("Unexpected script tag. {tag_header:?}");
                    // panic!("Unexpected script tag.");
                }
                on_meta_data = Some((tag_header, bytes.clone(), previous_tag_size.clone()));

                let flv_tag = FlvTag {
                    header: tag_header,
                    data: TagDataHeader::Script(tag_data)
                };
                flv_tag
            }
        };
        match &flv_tag {
            FlvTag{ data: TagDataHeader::Video { frame_type: FrameType::Key, ..}, ..} => {
                match segment {
                    Segment::Time(duration) => {
                        if duration <= Duration::from_millis((flv_tag.header.timestamp - first_tag_time) as u64) {
                            first_tag_time = flv_tag.header.timestamp;
                            file_index += 1;
                            let new_file_name = format!("{file_name}{file_index}");
                            out = create_flv_file(&new_file_name)?;
                            let on_meta_data = on_meta_data.as_ref().unwrap();
                            // onMetaData
                            write_tag_header(&mut out, &on_meta_data.0)?;
                            out.write(&on_meta_data.1)?;
                            out.write(&on_meta_data.2)?;
                            // AACSequenceHeader
                            let aac_sequence_header = aac_sequence_header.as_ref().unwrap();
                            write_tag_header(&mut out, &aac_sequence_header.0)?;
                            out.write(&aac_sequence_header.1)?;
                            out.write(&aac_sequence_header.2)?;
                            // H264SequenceHeader
                            let h264_sequence_header = h264_sequence_header.as_ref().unwrap();
                            write_tag_header(&mut out, &h264_sequence_header.0)?;
                            out.write(&h264_sequence_header.1)?;
                            out.write(&h264_sequence_header.2)?;
                            info!("{new_file_name} time splitting.");

                            // let file = std::fs::File::create(new_file_name + "_flv.json")?;
                            // writer = BufWriter::new(file);
                        }
                    }
                    Segment::Size(file_size) => {
                        if downloaded_size >= file_size {
                            downloaded_size = 9 + 4;
                            file_index += 1;
                            let new_file_name = format!("{file_name}{file_index}");
                            out = create_flv_file(&new_file_name)?;
                            let on_meta_data = on_meta_data.as_ref().unwrap();
                            // onMetaData
                            write_tag_header(&mut out, &on_meta_data.0)?;
                            out.write(&on_meta_data.1)?;
                            out.write(&on_meta_data.2)?;
                            // AACSequenceHeader
                            let aac_sequence_header = aac_sequence_header.as_ref().unwrap();
                            // (*aac_sequence_header).0.timestamp = on_meta_data.0.timestamp + 36000000;
                            write_tag_header(&mut out, &aac_sequence_header.0)?;
                            out.write(&aac_sequence_header.1)?;
                            out.write(&aac_sequence_header.2)?;
                            // H264SequenceHeader
                            let h264_sequence_header = h264_sequence_header.as_ref().unwrap();
                            // (*h264_sequence_header).0.timestamp = on_meta_data.0.timestamp + 36000000;
                            write_tag_header(&mut out, &h264_sequence_header.0)?;
                            out.write(&h264_sequence_header.1)?;
                            out.write(&h264_sequence_header.2)?;
                            info!("{new_file_name} size splitting.");

                            // let file = std::fs::File::create(new_file_name + "_flv.json")?;
                            // writer = BufWriter::new(file);
                        }
                    }
                }
                for (tag_header, flv_tag_data, previous_tag_size_bytes) in &flv_tags_cache {
                    if tag_header.timestamp < prev_timestamp {
                        warn!("Non-monotonous DTS in output stream; previous: {prev_timestamp}, current: {};", tag_header.timestamp);
                    }
                    write_tag_header(&mut out, tag_header)?;
                    out.write(flv_tag_data)?;
                    out.write(previous_tag_size_bytes)?;
                    downloaded_size += (11 + tag_header.data_size + 4) as u64;
                    prev_timestamp = tag_header.timestamp
                    // println!("{downloaded_size}");
                }
                flv_tags_cache.clear();
                flv_tags_cache.push((tag_header, bytes.clone(), previous_tag_size.clone()));
            }
            _ => {
                flv_tags_cache.push((tag_header, bytes.clone(), previous_tag_size.clone()));
            }
        }
        // flv_writer::to_json(&mut writer, &flv_tag)?;
    }
    Ok(())
}


pub fn map_parse_err<'a, T>(i_result: IResult<&'a [u8], T>, msg: &str) -> core::result::Result<(&'a [u8], T), crate::error::Error> {
    match i_result {
        Ok((i, res)) => {
            Ok((i, res))
        }
        Err(nom::Err::Incomplete(needed)) => {
            Err(crate::error::Error::NomIncomplete(msg.to_string(), needed))
        }
        Err(Err::Error(e)) => {
            panic!("parse {msg} err: {e:?}")
        }
        Err(Err::Failure(f)) => {
            panic!("{msg} Failure: {f:?}")
        }
    }
}

pub struct Connection {
    resp: Response,
    buffer: BytesMut,
}

impl Connection {
    pub(crate) fn new(resp: Response) -> Connection {
        Connection{
            resp,
            buffer: BytesMut::with_capacity(8 * 1024)
        }
    }

    fn read_frame(&mut self, chunk_size: usize) -> std::io::Result<Bytes> {
        let mut buf = [0u8; 8 * 1024];
        loop {
            if chunk_size <= self.buffer.len() {
                let bytes = Bytes::copy_from_slice(&self.buffer[..chunk_size]);
                self.buffer.advance(chunk_size as usize);
                return Ok(bytes)
            }
            // BytesMut::with_capacity(0).deref_mut()
            // tokio::fs::File::open("").read()
            let n = match self.resp.read(&mut buf) {
                Ok(n) => n,
                Err(e) if e.kind() == ErrorKind::Interrupted => continue,
                Err(e) => return Err(e),
            };

            if n == 0 {
                return Ok(self.buffer.split().freeze())
            }
            self.buffer.put_slice(&buf[..n]);
        }
    }
}

#[cfg(test)]
mod tests {
    use std::ops::Deref;
    use anyhow::Result;
    use bytes::{Buf, BufMut, BytesMut};
    use crate::downloader::httpflv::download;

    #[test]
    fn byte_it_works() -> Result<()> {
        let mut bb = bytes::BytesMut::with_capacity(10);
        println!("chunk {:?}", bb.chunk());
        println!("capacity {}", bb.capacity());
        bb.put( &b"hello"[..]);
        println!("chunk {:?}", bb.chunk());
        println!("remaining {}", bb.remaining());
        bb.advance(5);
        println!("capacity {}", bb.capacity());
        println!("chunk {:?}", bb.chunk());
        println!("remaining {}", bb.remaining());
        bb.put( &b"hello"[..]);
        bb.put( &b"hello"[..]);
        println!("chunk {:?}", bb.chunk());
        println!("capacity {}", bb.capacity());
        println!("remaining {}", bb.remaining());

        let mut buf = BytesMut::with_capacity(11);
        buf.put(&b"hello world"[..]);

        let other = buf.split();
        // buf.advance_mut()

        assert!(buf.is_empty());
        assert_eq!(0, buf.capacity());
        assert_eq!(11, other.capacity());
        assert_eq!(other, b"hello world"[..]);

        Ok(())
    }

    #[test]
    fn it_works() -> Result<()> {
        // download(
        //     "test.flv")?;
        Ok(())
    }
}