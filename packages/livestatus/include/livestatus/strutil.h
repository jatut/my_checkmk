// Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
// This file is part of Checkmk (https://checkmk.com). It is subject to the
// terms and conditions defined in the file COPYING, which is part of this
// source code package.

#ifndef strutil_h
#define strutil_h

char *next_token(char **c, char delim);
const char *safe_next_token(char **c, char delim);

#endif  // strutil_h
