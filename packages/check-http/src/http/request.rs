// Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
// This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
// conditions defined in the file COPYING, which is part of this source code package.

use bytes::Bytes;
use encoding_rs::{Encoding, UTF_8};
use mime::Mime;
use reqwest::{
    header::{HeaderMap, HeaderName, HeaderValue, CONTENT_TYPE},
    tls::TlsInfo,
    Client, Method, RequestBuilder, Result as ReqwestResult, StatusCode, Url, Version,
};

pub struct RequestConfig {
    pub url: Url,
    pub method: Method,
    pub version: Option<Version>,
    pub headers: Vec<(HeaderName, HeaderValue)>,
    pub body: Option<String>,
    pub content_type: Option<HeaderValue>,
    pub auth_user: Option<String>,
    pub auth_pw: Option<String>,
    pub without_body: bool,
    pub token_auth: Option<(HeaderName, HeaderValue)>,
}

pub struct ProcessedResponse {
    pub version: Version,
    pub status: StatusCode,
    pub headers: HeaderMap,
    pub body: Option<ReqwestResult<Body>>,
    pub final_url: Url,
    pub tls_info: Option<TlsInfo>,
}

#[cfg_attr(test, derive(PartialEq, Debug))]
pub struct Body {
    pub text: String,
    pub length: usize,
}

pub async fn send(client: Client, cfg: RequestConfig) -> ReqwestResult<ProcessedResponse> {
    let fetch_body = !cfg.without_body;

    let mut response = prepare_request(client, cfg).send().await?;

    let headers = response.headers().to_owned();
    let version = response.version();
    let status = response.status();
    let final_url = response.url().clone();
    let tls_info = response.extensions_mut().remove::<TlsInfo>();
    let body = if fetch_body {
        Some(process_body(response.bytes().await, &headers))
    } else {
        None
    };

    Ok(ProcessedResponse {
        version,
        status,
        headers,
        body,
        final_url,
        tls_info,
    })
}

fn prepare_request(client: Client, request_cfg: RequestConfig) -> RequestBuilder {
    let mut headers = HeaderMap::from_iter(request_cfg.headers);
    if let Some((token_header, token_key)) = request_cfg.token_auth {
        headers.insert(token_header, token_key);
    }
    if let Some(content_type) = request_cfg.content_type {
        headers.insert(CONTENT_TYPE, content_type);
    }

    let req = client
        .request(request_cfg.method, request_cfg.url)
        .headers(headers);

    let req = if let Some(version) = request_cfg.version {
        req.version(version)
    } else {
        req
    };

    let req = if let Some(body) = request_cfg.body {
        req.body(body)
    } else {
        req
    };

    if let Some(user) = request_cfg.auth_user {
        req.basic_auth(user, request_cfg.auth_pw)
    } else {
        req
    }
}

// We can't rely on the "content-length" header in general, so we need the raw body to determine
// the content length in bytes.
// For later processing, we may also need the body as text.
// However, Reqwest doesn't let us access the body as bytes before decoding to String.
// The code from this function is borrowed from reqwest::async_impl::response::Response::text_with_charset
// and enables us to get the length *and* the text.
fn process_body(bytes: ReqwestResult<Bytes>, headers: &HeaderMap) -> ReqwestResult<Body> {
    let bytes = bytes?;

    let length = bytes.len();
    let content_type = headers
        .get(CONTENT_TYPE)
        .and_then(|value| value.to_str().ok())
        .and_then(|value| value.parse::<Mime>().ok());
    let encoding = content_type
        .as_ref()
        .and_then(|mime| mime.get_param("charset").map(|charset| charset.as_str()))
        .and_then(|name| Encoding::for_label(name.as_bytes()))
        .unwrap_or(UTF_8);

    let (text, _, _) = encoding.decode(&bytes);

    Ok(Body {
        text: text.into_owned(),
        length,
    })
}
