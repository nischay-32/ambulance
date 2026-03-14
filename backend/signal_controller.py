from geopy.distance import geodesic
import math

# ── Major Bangalore signalised junctions ─────────────────────────────────────
# (lat, lng, name)
BANGALORE_JUNCTIONS = [
    # Central / CBD
    (12.9762, 77.5929, "Majestic"),
    (12.9716, 77.5946, "City Market"),
    (12.9714, 77.6035, "Richmond Circle"),
    (12.9698, 77.6088, "Lalbagh West Gate"),
    (12.9658, 77.5958, "Jayanagar 4th Block"),
    (12.9634, 77.6015, "Jayanagar Shopping Complex"),
    (12.9756, 77.6102, "Trinity Circle"),
    (12.9800, 77.6084, "Ulsoor"),
    (12.9784, 77.6025, "MG Road"),
    (12.9750, 77.6074, "Brigade Road"),
    (12.9833, 77.6101, "Halasuru"),
    (12.9890, 77.6095, "Indiranagar 100ft Road"),
    (12.9856, 77.6408, "Domlur"),
    (12.9822, 77.6472, "Marathahalli Bridge"),
    (12.9591, 77.6974, "Whitefield Main Junction"),
    (12.9698, 77.7472, "ITPL Main Road"),
    (12.9352, 77.6245, "BTM Layout"),
    (12.9153, 77.6101, "Electronic City Phase 1"),
    (12.8958, 77.6012, "Electronic City Phase 2"),
    (12.9276, 77.5835, "JP Nagar"),
    (12.9121, 77.5988, "Bannerghatta Road"),
    (12.9517, 77.5755, "Basavanagudi"),
    (12.9630, 77.5767, "NR Colony"),
    # North
    (13.0358, 77.5970, "Hebbal Flyover"),
    (13.0452, 77.6104, "Nagawara"),
    (13.0215, 77.5850, "Mathikere"),
    (13.0137, 77.5564, "Yeshwanthpur"),
    (13.0271, 77.5649, "Rajajinagar"),
    (12.9993, 77.5550, "Chord Road Junction"),
    (13.0081, 77.5720, "Vijayanagar"),
    (13.0350, 77.5750, "Peenya"),
    (13.0600, 77.5950, "Yelahanka"),
    (13.0670, 77.6200, "Yelahanka New Town"),
    (13.1000, 77.6100, "Devanahalli Road"),
    # South
    (12.9268, 77.5951, "Silk Board Junction"),
    (12.9190, 77.6221, "HSR Layout"),
    (12.9022, 77.6346, "Harlur"),
    (12.9456, 77.6170, "Ejipura"),
    (12.9382, 77.6124, "Koramangala"),
    (12.9500, 77.6270, "Koramangala 6th Block"),
    (12.9271, 77.5651, "Banashankari"),
    (12.9195, 77.5485, "Uttarahalli"),
    (12.8900, 77.5800, "Kengeri"),
    (12.9410, 77.5420, "Rajarajeshwari Nagar"),
    # East
    (13.0050, 77.6470, "KR Puram Bridge"),
    (12.9921, 77.6613, "Tin Factory"),
    (12.9768, 77.7101, "Hoodi"),
    (12.9632, 77.7245, "AECS Layout"),
    (13.0200, 77.6900, "Banaswadi"),
    (13.0090, 77.6600, "Ramamurthy Nagar"),
    # West
    (12.9756, 77.5450, "Rajajinagar West"),
    (12.9849, 77.5348, "Nagarbhavi"),
    (12.9968, 77.5100, "Kengeri Satellite Town"),
    (12.9612, 77.5219, "Mysore Road"),
    # Outer Ring Road
    (12.9550, 77.6950, "Marathahalli ORR"),
    (12.9270, 77.6850, "Sarjapur ORR"),
    (13.0190, 77.6940, "Varthur"),
    (12.9820, 77.7050, "Kadugodi"),
    (13.0420, 77.6620, "Banaswadi ORR"),
    (13.0650, 77.6000, "Bellary Road"),
    (13.0180, 77.5240, "Tumkur Road"),
    # Additional
    (12.9950, 77.6280, "Indiranagar CMH Road"),
    (12.9715, 77.6398, "Old Airport Road"),
    (12.9912, 77.5782, "Sadashivanagar"),
    (12.9857, 77.5691, "Mehkri Circle"),
    (12.9923, 77.5883, "Palace Grounds"),
    (12.9580, 77.6430, "Koramangala ORR"),
    (12.9430, 77.5730, "Girinagar"),
    (12.9723, 77.6564, "Domlur ORR"),
    (12.9500, 77.6640, "HSR ORR"),
    (13.0310, 77.5450, "Peenya Industrial"),
    (12.9880, 77.7210, "Whitefield Road"),
    (12.9791, 77.5913, "Gubbi Thotadappa Rd"),
    (12.9800, 77.6200, "Halasuru Lake Rd"),
    (12.9600, 77.6300, "HSR 27th Main"),
]

# How close a junction must be to a route point to be included (metres)
SNAP_RADIUS_M = 180


def _bearing_degrees(p1, p2):
    """Compass bearing (0=N, 90=E) from p1→p2."""
    lat1 = math.radians(p1[0]); lat2 = math.radians(p2[0])
    dLng = math.radians(p2[1] - p1[1])
    y = math.sin(dLng) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLng)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _offset_point(lat, lng, bearing_deg, distance_m):
    """Return a point offset `distance_m` metres in `bearing_deg` direction."""
    R = 6371000.0
    b = math.radians(bearing_deg)
    d = distance_m / R
    lat1 = math.radians(lat)
    lng1 = math.radians(lng)
    lat2 = math.asin(math.sin(lat1) * math.cos(d) +
                     math.cos(lat1) * math.sin(d) * math.cos(b))
    lng2 = lng1 + math.atan2(math.sin(b) * math.sin(d) * math.cos(lat1),
                              math.cos(d) - math.sin(lat1) * math.sin(lat2))
    return math.degrees(lat2), math.degrees(lng2)


class SignalController:
    def __init__(self):
        self.signals = []

    # ── public ─────────────────────────────────────────────────────────────────

    def initialize_signals(self, route_points, steps):
        """
        Build signal groups only for Bangalore junctions that lie on the route.

        Per matched junction we create 3 signals:
          • route   – on the ambulance's path         → turns GREEN on approach
          • cross_a – perpendicular direction A        → turns RED  on approach
          • cross_b – perpendicular direction B        → turns RED  on approach

        Cross signals are placed 12 m either side of the junction centre on
        the perpendicular axis so they are visually distinct on the map.
        """
        self.signals = []

        if not route_points:
            return self.signals

        # ── 1. Find the local travel bearing at each route point ──────────────
        # We'll use it to compute perpendicular offsets for cross signals.
        def route_bearing_near(jlat, jlng):
            """Return travel bearing at the closest route point."""
            best_idx, best_d = 0, float('inf')
            for i, rp in enumerate(route_points):
                d = geodesic((jlat, jlng), (rp['lat'], rp['lng'])).meters
                if d < best_d:
                    best_d, best_idx = d, i
            # Use bearing from prev→next point for stability
            i = best_idx
            if i == 0:
                p1 = route_points[0]; p2 = route_points[1] if len(route_points) > 1 else p1
            elif i >= len(route_points) - 1:
                p1 = route_points[-2]; p2 = route_points[-1]
            else:
                p1 = route_points[i - 1]; p2 = route_points[i + 1]
            return _bearing_degrees(
                (p1['lat'], p1['lng']),
                (p2['lat'], p2['lng'])
            )

        # ── 2. Match junctions to route ──────────────────────────────────────
        seen_junctions = set()

        for j_idx, (jlat, jlng, jname) in enumerate(BANGALORE_JUNCTIONS):
            # Check if this junction is within SNAP_RADIUS_M of any route point
            on_route = False
            for rp in route_points:
                if geodesic((jlat, jlng), (rp['lat'], rp['lng'])).meters <= SNAP_RADIUS_M:
                    on_route = True
                    break

            if not on_route:
                continue

            # De-duplicate (two junctions very close together)
            key = f"{round(jlat, 3)},{round(jlng, 3)}"
            if key in seen_junctions:
                continue
            seen_junctions.add(key)

            travel_bearing = route_bearing_near(jlat, jlng)
            perp_a = (travel_bearing + 90)  % 360   # right side of road
            perp_b = (travel_bearing + 270) % 360   # left  side of road

            # Cross signal positions: 12 m either side of junction centre
            ca_lat, ca_lng = _offset_point(jlat, jlng, perp_a, 12)
            cb_lat, cb_lng = _offset_point(jlat, jlng, perp_b, 12)

            base = f"j{j_idx}"

            # Route signal — sits right at the junction
            self.signals.append({
                "id":    f"{base}_route",
                "lat":   jlat,
                "lng":   jlng,
                "name":  jname,
                "state": "red",      # normal city state
                "phase": "normal",   # normal | prepare | active | reset
                "type":  "route",
                "distance_to_amb": float('inf'),
                "eta":             float('inf'),
            })

            # Cross signal A (right perpendicular)
            self.signals.append({
                "id":    f"{base}_cross_a",
                "lat":   ca_lat,
                "lng":   ca_lng,
                "name":  f"{jname} cross",
                "state": "green",
                "phase": "normal",
                "type":  "cross",
                "distance_to_amb": float('inf'),
                "eta":             float('inf'),
            })

            # Cross signal B (left perpendicular)
            self.signals.append({
                "id":    f"{base}_cross_b",
                "lat":   cb_lat,
                "lng":   cb_lng,
                "name":  f"{jname} cross",
                "state": "green",
                "phase": "normal",
                "type":  "cross",
                "distance_to_amb": float('inf'),
                "eta":             float('inf'),
            })

        print(f"[SignalController] {len(seen_junctions)} junctions on route → "
              f"{len(self.signals)} signals created.")
        return self.signals

    # ── Green Corridor state machine ──────────────────────────────────────────
    #
    # Zone thresholds (distance from ambulance to signal):
    #   PREPARE  : 600–1200 m ahead   → route = amber,   cross = green  (warning)
    #   ACTIVE   : 0–600 m ahead      → route = GREEN,   cross = RED    (clear path)
    #   HOLD     : 0–300 m behind     → keep active state (no flicker)
    #   RESET    : > 300 m behind     → route = red,     cross = green  (normal)
    #
    # "Ahead" vs "behind" is determined by comparing the ambulance's projected
    # forward vector with the vector ambulance→signal.

    PREPARE_NEAR  =  600   # m
    PREPARE_FAR   = 1200   # m
    ACTIVE_DIST   =  600   # m
    ACTIVE_ETA    =   25   # s
    HOLD_BEHIND   =  300   # m
    RESET_BEHIND  =  300   # m

    def update_signals(self, ambulance_location, ambulance_speed_mps=30):
        amb = ambulance_location

        for sig in self.signals:
            dist = geodesic(
                (amb["lat"], amb["lng"]),
                (sig["lat"], sig["lng"])
            ).meters
            eta = dist / max(1, ambulance_speed_mps)

            sig["distance_to_amb"] = dist
            sig["eta"]             = eta

            if sig["type"] == "route":
                self._update_route_signal(sig, dist, eta, ambulance_speed_mps)
            elif sig["type"] == "cross":
                # Cross signals mirror the phase of their paired route signal.
                # We locate the sibling route signal by ID convention.
                base = sig["id"].rsplit("_cross", 1)[0]
                route_sig = next(
                    (s for s in self.signals if s["id"] == f"{base}_route"), None
                )
                if route_sig:
                    self._update_cross_signal(sig, route_sig["phase"])

        return self.signals

    # ── internal helpers ──────────────────────────────────────────────────────

    def _update_route_signal(self, sig, dist, eta, speed):
        phase = sig["phase"]

        if dist <= self.ACTIVE_DIST and eta <= self.ACTIVE_ETA:
            # Ambulance is close and approaching fast → open corridor
            sig["phase"] = "active"
            sig["state"] = "green"

        elif dist <= self.PREPARE_FAR and phase == "normal":
            # Ambulance is in the prepare window → amber warning
            sig["phase"] = "prepare"
            sig["state"] = "amber"

        elif phase == "active" and dist > self.HOLD_BEHIND:
            # Ambulance has passed and moved away → reset
            sig["phase"] = "reset"
            sig["state"] = "red"

        elif phase == "reset" and dist > 800:
            # Fully back to normal city cycle
            sig["phase"] = "normal"
            sig["state"] = "red"

        # If phase == "prepare" and dist already dropped below ACTIVE_DIST,
        # the first branch above will fire. No explicit transition needed.

    def _update_cross_signal(self, sig, route_phase):
        if route_phase == "active":
            sig["phase"] = "active"
            sig["state"] = "red"    # cross traffic STOPPED
        elif route_phase == "prepare":
            sig["phase"] = "prepare"
            sig["state"] = "amber"  # cross traffic warned
        elif route_phase in ("reset", "normal"):
            sig["phase"] = route_phase
            sig["state"] = "green"  # cross traffic flows freely