from bletracking.db_update import db_update_when_tracker_is_out, db_update_when_tracker_is_in


def check_area_of_tracker(area, tracker):
    min_x = area["x"]
    min_y = area["y"]

    max_x = area["x"] + area["width"]
    max_y = area["y"] - (area["height"] * 1.75)

    tracker_x = tracker["smoothedPosition"][0]
    tracker_y = tracker["smoothedPosition"][1]

    is_in_x_area = min_x <= tracker_x <= max_x
    is_in_y_area = max_y <= tracker_y <= min_y

    is_in_area = is_in_x_area and is_in_y_area
    is_in_area = "IN" if is_in_area else "OUT"
    prepared_data = {"id": tracker["id"], "is_in_area": is_in_area, "mcid": area["mcid"]}
    return prepared_data


def check_area_entering(data_from_qpe, area_list):
    prepared_data = []
    for tracker in data_from_qpe["tags"]:
        checked_area = [check_area_of_tracker(area, tracker) for area in area_list]
        prepared_data = prepared_data + checked_area

    trackers_in_area = [data for data in prepared_data if data["is_in_area"] == "IN"]
    trackers_out_of_area = [data for data in prepared_data]
    for item in trackers_out_of_area:
        db_update_when_tracker_is_out(item)
    for item in trackers_in_area:
        db_update_when_tracker_is_in(item)
