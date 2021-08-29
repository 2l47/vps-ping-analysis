# VPS Ping Analysis (VPA)

## About VPA

VPA uses the [Where's It Up API](https://wheresitup.com/) to ping lists of VPS datacenter locations to determine how well they can each serve different regions with acceptably low network latency. Additionally, VPA is capable of generating maps that display the average ping values in each city.

My goal here was to determine what hosting provider and datacenter region would provide the best experience for Team Fortress 2 players. It shouldn't be hard to adapt the script to other needs.

At the time of writing, WIU offers 10,000 free credits upon signup, which makes it easy to try out.

## VPA's principle of operation

To illustrate: one can create a job through the WIU API that sends 100 ICMP ping probes to [Linode](https://www.linode.com/)'s [Dallas speedtest server](http://speedtest.dallas.linode.com) from each of the 80 servers WIU has in US and Canadian cities. After receiving the job results, they can then categorize those cities into ranked ranges of ping values.

```
perfect ping areas: [('asheville', '26.143'), ('atlanta', '19.044'), ('austin', '24.970'), ('charlotte', '24.392'), ('cheyenne', '29.896'), ('chicago', '24.686'), ('coloradosprings', '21.819'), ('dallas', '5.711'), ('denver', '20.271'), ('desmoines', '19.068'), ('detroit', '29.840'), ('houston', '6.751'), ('jackson', '25.151'), ('jacksonville', '25.216'), ('kansascity', '11.502'), ('lincoln', '16.780'), ('memphis', '17.365'), ('minneapolis', '28.626'), ('neworleans', '13.400'), ('oklahomacity', '8.240'), ('orlando', '29.762'), ('phoenix', '23.765'), ('sanantonio', '14.054'), ('southbend', '23.359'), ('stlouis', '22.697')]
satisfactory ping areas: [('albany', '43.884'), ('albuquerque', '36.491'), ('baltimore', '37.215'), ('berkeleysprings', '38.964'), ('brunswick', '49.290'), ('buffalo', '33.834'), ('cincinnati', '37.010'), ('cleveland', '33.899'), ('columbus', '44.706'), ('cromwell', '42.443'), ('fremont', '42.756'), ('greenbay', '42.349'), ('indianapolis', '40.113'), ('knoxville', '58.103'), ('lansing', '30.473'), ('lasvegas', '38.132'), ('losangeles', '42.644'), ('manhattan', '35.094'), ('miami', '35.039'), ('milwaukee', '47.953'), ('monticello', '30.394'), ('montreal', '43.998'), ('newyork', '37.461'), ('ottawa', '43.152'), ('philadelphia', '40.292'), ('piscataway', '35.621'), ('pittsburgh', '37.427'), ('portland', '51.887'), ('quebeccity', '43.454'), ('raleigh', '37.561'), ('redding', '46.982'), ('sacramento', '43.508'), ('salem', '45.310'), ('saltlakecity', '45.687'), ('sandiego', '39.917'), ('sanfrancisco', '43.543'), ('sanjose', '40.156'), ('saskatoon', '43.625'), ('savannah', '45.738'), ('scranton', '42.126'), ('seattle', '56.356'), ('secaucus', '39.746'), ('syracuse', '38.737'), ('tampa', '34.202'), ('toledo', '36.581'), ('toronto', '39.763'), ('vancouver', '56.364'), ('washington', '32.252'), ('winnipeg', '34.144')]
uncomfortable ping areas: [('calgary', '77.627'), ('edmonton', '86.799'), ('roseburg', '60.159')]
unplayable ping areas: [('honolulu', '90.429')]
```

## Using VPA

VPA provides a function that allows you to perform these tests across multiple datacenter locations as well as on different hosting providers:

```
def test_datacenters(datacenter_names,
                    uri_prefix,
                    uri_suffix,
                    from_locations,
                    hosting_provider=None,
                    continents=None,
                    reuse_job=None,
                    interactive_map=False):
```

For example usage, see the end of main.py.

## Software Dependencies

### Install the official [WIU Python library](https://wheresitup.com/docs/#clients-and-examples)
```
git clone --depth 1 https://github.com/WonderNetwork/wiuppy
pip3 install ./wiuppy/
rm -rf ./wiuppy/
```

### Install the development headers needed to build cartopy
`sudo apt install libgeos-dev libproj-dev`

### Install cartopy, geopandas, and matplotlib

`pip3 install cartopy geopandas matplotlib`

If you encounter a crash when creating the map, see https://github.com/Toblerity/Shapely/issues/1187

## Authenticating with the WIU API

Create a config file at ~/.wiuppy containing your credentials like so:
```
[Auth]
client=abcdef
token=123456
```
