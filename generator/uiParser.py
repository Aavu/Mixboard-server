# Parse data from the front end 

import numpy as np
import json
from .modules.enums import StemType, SongSection, State


class Item:
    def __init__(self, song_id: str = None, item: dict = None):
        if item is not None:
            self.song_id = item.get("songId")
        else:
            self.song_id = song_id


class Region:
    def __init__(self, user_id: str, session_id: str, stem_type: StemType, region_id: str = None, x: int = None,
                 w: int = None, state: State = None, song_id: str = None,
                 region_dict: dict = None):
        self.user_id = user_id
        self.session_id = session_id
        self.stem_type = stem_type
        if region_dict is not None:
            self.w = region_dict.get("w")
            self.id = region_dict.get("id")
            self.state = State[region_dict.get("state")]
            self.x = region_dict.get("x")
            self.item = Item(item=region_dict.get("item"))

        else:
            self.id = region_id
            self.x = x
            self.w = w
            self.state = state
            self.item = Item(song_id=song_id)

    def __str__(self):
        return f"id: {self.id}, x: {self.x}, w: {self.w}, state: {self.state.value}, song_id: {self.item.song_id}"


class Layout:
    def __init__(self, user_id: str, session_id: str, stem_type: StemType, regions: [Region] = None,
                 regions_dict: [dict] = None):
        self.regions = {}
        if regions_dict is not None:
            for reg in regions_dict:
                region = Region(user_id=user_id, session_id=session_id, stem_type=stem_type, region_dict=reg)
                self.regions[region.id] = region
        else:
            for region in regions:
                self.regions[region.id] = region

    def __str__(self):
        ret = "Regions:\n"
        for reg in self.regions:
            ret += reg.__str__() + "\n"
        return ret


class Stem:
    def __init__(self, user_id: str, session_id: str, stem_type: StemType, layout: Layout = None,
                 layout_dict: dict = None):
        self.stem_type = stem_type
        if layout_dict is not None:
            self.layout = Layout(user_id=user_id, session_id=session_id, stem_type=stem_type,
                                 regions_dict=layout_dict.get("layout"))
        else:
            self.layout = layout

    def __str__(self):
        return f"{self.stem_type} : {self.layout.__str__()} \n"

    @property
    def regions(self) -> {str: Region}:
        return self.layout.regions


class UiParser:
    def __init__(self, ui_data):
        self.ui_data = ui_data
        self.data = ui_data.get("data")

        self.regions = {}
        self.stems = {}

        for t in StemType:
            stem_id = self.__get_stem_id(t)
            self.stems[t] = Stem(user_id=self.user_id, session_id=self.session_id, stem_type=t,
                                 layout_dict=self.data.get(stem_id))
            self.regions.update(self.stems[t].regions)

    @staticmethod
    def __get_stem_id(stem_type) -> str:
        if stem_type is StemType.Other:
            return "1"
        elif stem_type is StemType.Bass:
            return "2"
        elif stem_type is StemType.Drums:
            return "3"
        return "0"

    @property
    def user_id(self):
        usr_id = self.ui_data.get("email")
        if usr_id:
            return usr_id
        return "unknown"

    @property
    def session_id(self) -> str:
        sess_id: str = self.ui_data.get("sessionId")
        if sess_id:
            return sess_id
        return "unknown"

    @property
    def tempo(self) -> float:
        return self.ui_data.get("tempo")

    @property
    def pitch(self):
        return self.ui_data.get("pitch")

    def set_tempo(self, tempo: float):
        self.ui_data["tempo"] = tempo

    def set_pitch(self, pitch):
        self.ui_data["pitch"] = pitch

    @property
    def previous_session_id(self) -> str or None:
        return self.ui_data.get("lastSessionId")

    @property
    def should_copy_last_session(self) -> bool:
        for region in self.regions.values():
            if region.state is State.Ready:
                return True

        return False

    def get_stem(self, stem_type) -> Stem:
        return self.stems.get(stem_type)

    def get_song_ids(self, stem_type, return_state=False):
        items = []
        regions = self.get_regions(stem_type)
        for region in regions.values():
            item = (region.item.song_id, region.state) if return_state else region.item.song_id
            items.append(item)
        return list(set(items))

    @staticmethod
    def get_song_id(region: Region):
        return region.item.song_id

    def get_num_of_blocks(self, stem_type):
        return len(self.get_regions(stem_type))

    def get_layout(self, stem_type: StemType) -> Layout:
        return self.get_stem(stem_type).layout

    def get_regions(self, stem_type: StemType = None, include_ready: bool = True) -> {str: Region}:
        ret_regions = {}
        in_regions = self.regions
        if stem_type is not None:
            in_regions = self.get_layout(stem_type).regions

        for key, region in in_regions.items():
            if region.state == State.New or include_ready:
                ret_regions[key] = region
        return ret_regions

    def get_start_bars(self, stem_type):
        regions = list(self.get_regions(stem_type).values())
        start_bars = np.zeros(len(regions), dtype=np.int32)
        for i in range(len(regions)):
            start_bars[i] = regions[i].x
        return start_bars

    def get_start_bar(self, region_id: str):
        return self.regions.get(region_id).x

    def get_end_bars(self, stem_type):
        start_bars = self.get_start_bars(stem_type)
        bar_lengths = self.get_bar_lengths(stem_type)
        return start_bars + bar_lengths

    def get_end_bar(self, region_id: str):
        start_bar = self.get_start_bar(region_id)
        bar_length = self.get_bar_length(region_id)
        return start_bar + bar_length

    def get_bar_lengths(self, stem_type):
        regions = list(self.get_regions(stem_type).values())
        bar_lengths = np.zeros(len(regions), dtype=np.int32)
        for i in range(len(regions)):
            bar_lengths[i] = regions[i].w
        return bar_lengths

    def get_bar_length(self, region_id: str):
        return self.regions.get(region_id).w

    @property
    def selected_songs(self):
        selected_songs = []
        for stemType in StemType:
            _song_ids = self.get_songs_in_track(stemType)
            print(_song_ids)
            selected_songs.extend(_song_ids)
        print(selected_songs)
        return list(set(selected_songs))

    def get_songs_in_track(self, stem_type: StemType):
        regions = self.get_regions(stem_type)
        song_ids = []
        for region in regions.values():
            song_ids.append(region.item.song_id)
        return list(set(song_ids))

    @property
    def vocal_tracks(self):
        selected_songs = set()
        _song_ids = self.get_song_ids(StemType.Vocals)
        selected_songs.update(_song_ids)
        return list(selected_songs)

    @property
    def song_duration(self):
        max_duration = 0
        for stemType in StemType:
            _lastStartBars = self.get_start_bars(stemType)
            _lastBarLength = self.get_bar_lengths(stemType)
            if _lastStartBars.size and _lastBarLength.size:  # Check if they are empty
                if _lastStartBars[-1] + _lastBarLength[-1] > max_duration:
                    max_duration = _lastStartBars[-1] + _lastBarLength[-1]
        return max_duration

    @property
    def should_sync_sections(self):
        section_sync = self.data.get("section_sync")
        if section_sync:
            return section_sync
        return False

    @property
    def should_link_lane(self):
        lane_link = self.data.get("lane_link")
        if lane_link:
            return lane_link
        return False


if __name__ == "__main__":
    inputData = json.load(open("./generator/stem_data.json"))
    parseStem = UiParser(inputData)

    print(parseStem.selected_songs)
