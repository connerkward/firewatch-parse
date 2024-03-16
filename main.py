from lxml import html
import re
from collections import defaultdict

tree1 = html.parse('http://peakbagging.com/Peak%20Lists/CA_Lookout1.html')
tree2 = html.parse('http://peakbagging.com/Peak%20Lists/CA_Lookout2.html')

tr_elements1 = tree1.xpath('//tr')
tr_elements2 = tree2.xpath('//tr')

selected_categories = ["ID", "LO", "NHLR", "County", "Topo Map", "Lookout Name",
                       "EL, ft.", "Latitude", "Longitude", "Forest",
                       "PID", "LO BM", "YR", "BM Name"]
selected_categories_set = set(selected_categories)

# print("SELECTED CATEGORIES")
# print(selected_categories)


def clean(string):
    return re.sub("\n|\t|\xa0", " ", string).strip()


# print("FILE1 CATEGORIES")
# print([clean(row.text_content()) for row in tr_elements1[3]])
# print("FILE2 CATEGORIES")
# print([clean(row.text_content()) for row in tr_elements2[3]])

file1_key_indexes = [i for i in range(len(tr_elements1[3])) if
                     clean(tr_elements1[3][i].text_content()) in selected_categories_set]
file2_key_indexes = [i for i in range(len(tr_elements2[3])) if
                     clean(tr_elements2[3][i].text_content()) in selected_categories_set]

# Lookout Status Codes:
# A = structure in good condition, capable of being staffed.
# B = Dilapidated and needs work, but standing.
# C = Badly damaged or falling down.
# AS = usually staffed by Forest Service or CDF.
# AV = staffed by volunteers.
# AR = A rental Lookout.
# A (LO site) is where the building has been removed and there may be no evidence remaining, or it's status may be unknown.

# use this for grouping
LO_code_ranking = {"A": 1, "B": 1, "C": 2, "AS": 1, "AV": 1, "AR": 2, }

# print("\nDATA")
data = dict()  # {ID : {row data}}
error_count = 0
# print("FILE 1")
# print([clean(tr_elements1[3][i].text_content()) for i in range(len(tr_elements1[3])) if i in file1_key_indexes])
for row in tr_elements1[4:]:
    # check if row has valid LO data
    if clean(row[5].text_content()) is not None and clean(row[5].text_content()) in LO_code_ranking.keys():
        # print([clean(row[i].text_content()) for i in range(len(row)) if i in file1_key_indexes])
        row_dict = {clean(tr_elements1[3][i].text_content()): clean(row[i].text_content()) for i in range(len(row)) if
                    i in file1_key_indexes}
        row_dict["LO RANKING GROUP"] = LO_code_ranking[clean(row[5].text_content())]
        data[clean(row[0].text_content())] = row_dict

# [print(val) for val in data.values()]
# print("FILE 2")
# print([clean(tr_elements2[3][i].text_content()) for i in range(len(tr_elements2[3])) if i in file2_key_indexes])
for row in tr_elements2[4:]:
    # check if row has valid LO data
    if clean(row[5].text_content()) is not None and clean(row[5].text_content()) in LO_code_ranking.keys():
        # print([clean(row[i].text_content()) for i in range(len(row)) if i in file2_key_indexes])
        # check if valid category index
        row_dict = {clean(tr_elements2[3][i].text_content()): clean(row[i].text_content()) for i in range(len(row)) if
                    i in file2_key_indexes}
        # assert that each value in the row_dict is equivalent to its value in "data" dict
        try:
            for key, value in row_dict.items():
                if key in data[row_dict["ID"]]:
                    try:
                        assert value == data[row_dict["ID"]][key], f"{value}, {data[row_dict['ID']][key]},{row_dict['ID']}"
                    except AssertionError as e:
                        data[row_dict["ID"]][key] = [data[row_dict["ID"]][key], value]
                        # print("Non matching data error, ", row_dict["ID"])
                        error_count += 1
                        # print(data[row_dict["ID"]])
                    # add in new categories

        except KeyError:
            # print("Missing from first error, ", row_dict["ID"])
            # data[row_dict["ID"]] = row_dict
            error_count += 1

        if row_dict["ID"] in data.keys():
            row_dict["LO RANKING GROUP"] = LO_code_ranking[clean(row[5].text_content())]
            for key in row_dict:
                data[clean(row[0].text_content())][key] = row_dict[key]


tahoe_counties = ["Nevada", "Placer", "El Dorado", "Amador", "Calaveras", "Tuolumme", "Mariposa", "Madera", "Alpine", "Butte", "Yuba"]
bay_counties = ["Lake", "Napa", "Sonoma", "Marin", "San Mateo", "Santa Clara", "Stanislaus", "San Benito", "Monterey", "Fresno", "Merced"]

# print("All Counties")
# print(sorted({loc["County"] for loc in data.values()}))

print("Original Dataset Sites: ", len(tr_elements1[4:]))
print("Total Valid Sites: ", len(data), "(Has LO rating)")
print(f"Counties Being Searched: {len(tahoe_counties)}")
print(sorted(tahoe_counties))
print(f"Total Nearby Sites: ", len([row for row in data.values() if row["County"] in tahoe_counties]))
valid_sites = sorted([row for row in data.values() if row["County"] in tahoe_counties], key=lambda x: x["LO RANKING GROUP"])  # filtered for LO rating, only contains relevant data

# from pyproj import Transformer
#
# from pyproj import Transformer
# from pyproj import Proj, transform
# p2 = Proj(init='epsg:4326')
#
# # no offsets
# p1 = Proj(init='epsg:4269')
#
# # method: coordinate frame
# p1cf = Proj(proj='latlong', ellps='GRS80', datum='NAD83', towgs84='-0.9956,1.9013,0.5215,-0.025915,-0.009426,-0.0011599,-0.00062')
#
# # method: position vector
# p1pv = Proj(proj='latlong', ellps='GRS80', datum='NAD83', towgs84='-0.9956,1.9013,0.5215,0.025915,0.009426,0.0011599,-0.00062')

# print(transform(p1, p2, 373621, 1213713))

# Lookout Status Codes:
# A = structure in good condition, capable of being staffed.
# B = Dilapidated and needs work, but standing.
# C = Badly damaged or falling down.
# AS = usually staffed by Forest Service or CDF.
# AV = staffed by volunteers.
# AR = A rental Lookout.
# A (LO site) is where the building has been removed and there may be no evidence remaining, or it's status may be unknown.

#LO_code_ranking = {"A": 1, "B": 1, "C": 2, "AS": 1, "AV": 1, "AR": 2, }

def english(siterating):
    transform = {"A":"structure in good condition, capable of being staffed.",
                "B": "Dilapidated and needs work, but standing.",
                "C": "Badly damaged or falling down.",
                "AS": "usually staffed by Forest Service or CDF.",
                "AV" :"staffed by volunteers.",
                "AR": "A rental Lookout."
                }
    return transform[siterating]

for site in valid_sites:
    print(site["Forest"], "Forest")
    gmaps_latlon_url = f"https://www.google.com/maps/search/?api=1&query={site['Latitude']}%2C{site['Longitude']}"
    gmaps_query_url = f"https://www.google.com/maps/search/?api=1&query={'+'.join(site['Lookout Name'].split()) + '+Lookout'}"
    print(site["Lookout Name"]+" Lookout,", site["County"] + " County")
    print(english(site["LO"]))
    # print(gmaps_latlon_url)
    print(gmaps_query_url)
    print()




