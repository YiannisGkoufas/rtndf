////////////////////////////////////////////////////////////////////////////
//
//  This file is part of rtndf
//
//  Copyright (c) 2016, Richard Barnett
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of
//  this software and associated documentation files (the "Software"), to deal in
//  the Software without restriction, including without limitation the rights to use,
//  copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
//  Software, and to permit persons to whom the Software is furnished to do so,
//  subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
//  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
//  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
//  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
//  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
//  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#ifndef _MODETDEFS_H_
#define _MODETDEFS_H_

//  meta defs for motion detect PPE

#define MODET_META_TYPE                 "modet"
#define MODET_META_REGIONS              "regions"           // the detected regions

//  each region entry looks like this

#define MODET_META_INDEX                "index"             // region index (0 - n in frame)
#define MODET_META_REGION_X             "x"                 // region left x coord
#define MODET_META_REGION_Y             "y"                 // region bottom y coord
#define MODET_META_REGION_W             "w"                 // region width
#define MODET_META_REGION_H             "h"                 // region height
#define MODET_META_JPEG                 "jpeg"              // the actual image segment in base64

#endif // _MODETDEFS_H_

