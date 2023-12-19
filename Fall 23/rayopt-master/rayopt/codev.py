#
#   rayopt - raytracing for optical imaging systems
#   Copyright (C) 2012 Robert Jordens <robert@joerdens.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import xml.etree.ElementTree as et

import numpy as np

from .material import CoefficientsMaterial
from .library_items import Material, Catalog


def register_parsers():
    Catalog.parsers[".xml"] = codevxml_read
    Material.parsers["codev"] = codevxml_to_material


def codevxml_read(file, session):
    cat = Catalog()
    data = cat.load(file)
    cat.type, cat.source, cat.format = "material", "codev", "codev"
    data = et.fromstring(data)
    cat.name = data.find("./Name").text
    cat.comment = data.find("./ID").text
    session.add(cat)
    for glass in data.iterfind("./Glasses/Glass"):
        l = Material()
        cat.materials.append(l)
        name = glass.find("./GlassName").text
        assert name.startswith(cat.comment), (cat.comment, name)
        l.name = name[len(cat.comment):]
        l.comment = glass.find("./NumericName").text
        l.status = int(glass.find("./Availability").text)
        l.data = et.tostring(glass)
    return cat


def codevxml_to_material(data, item=None):
    data = et.fromstring(data)
    mat = CoefficientsMaterial(coefficients=[])
    mat.typ = {
        "Standard Sellmeier": "sellmeier",
        "Glass Manufacturer Sellmeier": "sellmeier_squared_offset",
        "Laurent": "schott",
        "Glass Manufacturer Laurent": "schott",
        "Herzberger": "herzberger",
        "Cauchy": "conrady",
    }[data.find("./EquationType").text]
    mat.name = data.find("./GlassName").text[2:]
    mat.coefficients = np.array([
        float(_.text) for _ in data.iterfind(
            "./DispersionCoefficients/Coefficient")])
    return mat


def main():
    import argparse
    import zipfile
    import tempfile
    import shutil
    import os
    from .library import Library

    parser = argparse.ArgumentParser()
    parser.add_argument("location", nargs="?",
                        default="https://optics.synopsys.com/"
                        "support/cvdownloads/glasscatalogs_xml.zip")
    parser.add_argument("-f", "--file", action="store_true")
    parser.add_argument("-d", "--db", help="library database url",
                        default=None)
    parser.add_argument("-x", "--replace", action="store_true")
    opts = parser.parse_args()
    lib = Library(opts.db)

    if opts.file:
        f = opts.location
    else:
        import requests
        from six import BytesIO
        f = BytesIO(requests.get(opts.location).content)
    try:
        dir = tempfile.mkdtemp()
        with zipfile.ZipFile(f, "r") as file:
            for cat in file.namelist():
                if opts.replace:
                    p = os.path.splitext(os.path.basename(cat))[0]
                    for i in lib.session.query(Catalog).filter(
                        Catalog.source == "codev").filter(
                            Catalog.name == p):
                        lib.session.delete(i)
                lib.load(file.extract(cat, dir))
    finally:
        shutil.rmtree(dir)


if __name__ == "__main__":
    main()
