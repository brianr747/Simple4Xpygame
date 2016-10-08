"""
utils.py
Copyright 2016 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import math


def CalcDist(o1, o2):
    return math.sqrt(float(pow(o1.x - o2.x, 2)) + float(pow(o1.y - o2.y, 2)))

def ParseCommString(s):
    """Convert a string used in socket communications into a dict"""
    try:
        splitup = s.split("|")
        out = []
        for txt in splitup:
            if '=' not in txt:
                continue
            ddata = {}
            txt = txt.split(";")
            for elem in txt:
                elem = elem.split("=")
                if len(elem) < 2:
                    continue
                ddata[elem[0]] = elem[1]
            out.append(ddata)
        return out
    except:
        raise ValueError("Parse error")

