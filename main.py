#!/usr/bin/env python3

import cartopy.crs as ccrs
import configparser
import geopandas as gpd
import importlib
import matplotlib.pyplot as plt
import os
import sys
import wiuppy



# Load credentials and instantiate API
config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.wiuppy"))
client = config["Auth"]["client"]
token = config["Auth"]["token"]
api = wiuppy.WIU(client, token)


# Load WIU data
wiu_continents = set()
wiu_countries = set()
wiu_NA_servers = []
wiu_EU_servers = []
wiu_servers = api.servers()
for d in wiu_servers:
	wiu_continents.add(d["continent_name"])
	wiu_countries.add(d["country"])
	if d["country"] in ["United States", "Canada"]:
		wiu_NA_servers.append(d["name"])
	if d["continent_name"] == "Eurasia":
		wiu_EU_servers.append(d["name"])
print(f"WIU Continents: {wiu_continents}")
print(f"\nWIU Countries: {wiu_countries}")
print(f"\nWIU NA servers: {wiu_NA_servers}")
print(f"\nWIU EU servers: {wiu_EU_servers}")


# Define acceptable ping range criteria
ping_ranges = (
	{"name": "perfect", "range": range(0, 30)}, # 0 <= ping < 30
	{"name": "satisfactory", "range": range(30, 60)}, # 30 <= ping < 60
	{"name": "uncomfortable", "range": range(60, 90)}, # 60 <= ping < 90
	{"name": "unplayable", "range": range(90, sys.maxsize)} # 90 <= ping < sys.maxsize
)


def test_datacenters(datacenter_names, uri_prefix, uri_suffix, from_locations, hosting_provider=None, continents=None, reuse_job=None, interactive_map=False):
	if hosting_provider:
		hosting_provider = f" at {hosting_provider}"
		if continents:
			hosting_provider += f" ({', '.join(continents)})"
	for datacenter in datacenter_names:
		job = wiuppy.Job(api)
		if not reuse_job:
			full_uri = f"{uri_prefix}{datacenter}{uri_suffix}"
			print(f"{'=' * 8} Preparing job for {datacenter}{hosting_provider} ({full_uri})... {'=' * 8}")
			job.uri = full_uri
			job.servers = from_locations
			job.tests = ["ping"]
			# 100 pings at half-second intervals should take 50 seconds; we allot a reasonably generous deadline of 60 seconds
			job.options = {"ping": {"interval": 0.500, "count": 100, "timeout": 60}}

			# Submit the request and wait for the tests to finish
			print("Submitting job...")
			job.submit()
		else:
			job.id = reuse_job

		print("Waiting for job retrieval...")
		job.retrieve(poll=True)

		# Reset server lists for the new datacenter we're testing
		for designation in ping_ranges:
			designation["servers"] = []

		# Report the average ping time on all servers
		print(f"Collecting regional ping times to {datacenter}...")
		for (server, tests) in job.results["response"]["complete"].items():
			summary = tests["ping"]["summary"]["summary"]
			print(f"\n{server} -> {datacenter}")
			print(f"\t{summary['transmitted']} packets transmitted, {summary['received']} received, {summary['packetloss']} packet loss, time {summary['time']}")
			print(f"\trtt min/avg/max/mdev = {summary['min']}/{summary['avg']}/{summary['max']}/{summary['mdev']} ms")

			for designation in ping_ranges:
				if int(float(summary["avg"])) in designation["range"]:
					designation["servers"].append((server, summary["avg"]))
					break

		# Load world file
		world = gpd.read_file("data/ne_10m_admin_1_states_provinces.shp")
		if continents:
			world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
			new_world = None
			for c in continents:
				print(f"Looking for {c}")
				found = world[world.continent == c]
				if new_world is None:
					new_world = found
				else:
					new_world = new_world.append(found)
			world = new_world
		# Reproject to Mercator
		world = world.to_crs(epsg=3395)
		# This is our subplot
		ax2 = plt.subplot(projection=ccrs.epsg(3395))
		plt.title(f"Expected quality of regional latency for {datacenter}{hosting_provider}\n(Larger circles indicate better latency)")
		# Rendering options
		world.plot(
			legend = True,
			edgecolor = "black",
			color = "blue",
			linewidth = 0.25 if continents else 0.05,
			alpha = 0.25,
			ax = ax2
		)

		# Print results for this datacenter while generating the map
		for designation in ping_ranges:
			print(f"\n{designation['name']} ping areas: {designation['servers']}")
			for city, ping in designation["servers"]:
				# Calculate radii such that lower ping values are bigger circles, to visualize how well the datacenter covers the area
				radius = ((-200/90) * float(ping)) + 200
				# Get this city's coordinates and plot the point
				for s in wiu_servers:
					if s["name"] == city:
						latitude = float(s["latitude"])
						longitude = float(s["longitude"])
						# n_samples determines circle "roughness"
						ax2.tissot(rad_km=radius, lats=[latitude,], lons=[longitude,], n_samples=36)
						break

		# Display or save our map
		if interactive_map:
			plt.show()
		else:
			plt.savefig(f"{datacenter}{hosting_provider}.png", dpi=600 if continents else 2400)#, bbox_inches="tight")
		print("\n")

		# Get rid of world and plot stuff
		importlib.reload(plt)

		# We're assuming the provided job was for the first location in the list
		if reuse_job:
			break


# Declare Linode's speedtest subdomains
linode_NA_locations = "fremont dallas atlanta toronto1 newark".split()
linode_EU_locations = "london frankfurt".split()

# Declare Hetzner's speedtest subdomains
hetzner_EU_locations = "nbg fsn hel".split()


# Get ping times for Linode's North America datacenters
test_datacenters(linode_NA_locations, "http://speedtest.", ".linode.com", wiu_NA_servers, hosting_provider="Linode", continents=["North America"])

# Get ping times for Linode's EU datacenters
test_datacenters(linode_EU_locations, "http://speedtest.", ".linode.com", wiu_EU_servers, hosting_provider="Linode", continents=["Europe", "Asia"])

# Get ping times for Hetzner's EU datacenters
test_datacenters(hetzner_EU_locations, "http://", ".icmp.hetzner.com", wiu_EU_servers, hosting_provider="Hetzner", continents=["Europe", "Asia"])
