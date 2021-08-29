# tzim

Convert Tomboy / Gnote notes to zim notes

This is a version by Tim Jackson, substantially rewritten from earlier versions
by Bengt J. Olsson and Osamu Aoki. Amongst other benefits, it supports nested 
lists. (Internally, it uses an XML processer to parse the source notes
"properly" rather than converting them using regular expressions.)

## Requirements
Python 3.

## Usage

Execute the following:

```
 $ python3 /path/to/tzim.py --source-dir=[TOMBOY/GNOTE DIR] --dest-dir=[ZIM DIR]
```

This converts Tomboy / Gnote notes from TOMBODY/GNOTE DIR and puts the result in
ZIM DIR. Notes that are tagged with a label will be put in a subdirectory of
ZIM DIR.

You can import each page to `zim` one by one via `File` -> `Import page...`.

Also you can move this target directory content to some path where you keep
`zim` data using `cp` or `mc` commands.  Then restart `zim` and you are all
set.


## License

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

## Copyright

  * Copyright 2007,2008 Bengt J. Olsson
  * Copyright 2020      Osamu Aoki
  * Copyright 2021      Tim Jackson <tim@timj.co.uk>

## Repository

This python3 code is hosted at: https://github.com/timjackson/tzim

It is a mostly rewritten version of the code hosted at:
 https://github.com/osamuaoki/tzim

