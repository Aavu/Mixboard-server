<template>
  <div>
    <div class="container">
      <v-row style="margin-bottom: 4px" v-show="showInput">
        <input
          v-show="showInput"
          v-model="searchText"
          placeholder="Song/Artist"
          style="color: #33101c"
          type="text"
          @keyup="searchSongs"
        />
      </v-row>
      <div
        style="
          max-width: 240px;
          max-height: 500px;
          overflow-y: scroll;
          overflow-x: hidden;
        "
      >
        <div
          v-for="song in searchedsongList"
          :key="song.songId"
          :class="{ isSelected: selectedItem[song.songId] }"
          class="my-3"
          style="
            max-height: 200px;
            max-width: 100%;
            overflow: hidden;
            padding-bottom: 5px;
            border-bottom: 1px solid grey;
          "
          @click="changeSongSelection(song)"
        >
          <div class="row song-item">
            <div class="col-sm-6" style="text-transform: capitalize">
              <span>{{ song.songName }}</span>
              <br />
              <span class="font-weight-light text-muted"
                >{{ song.artistName }}
                <v-icon>mdi-check-underline</v-icon></span
              >
            </div>

            <div
              class="col-sm-5 col-xs-5 text-center"
              @mouseleave="mouseoffAlbum(song)"
              @mouseover="mouseonAlbum(song)"
            >
              <v-img
                :src="song.img_url"
                alt="image"
                blank-color="#ccc"
                style="height: auto"
              >
                <div
                  v-show="song.songId === mouseon_Album.songId"
                  class="album_overlay"
                >
                  <v-btn
                    v-show="song.preview_url !== null"
                    class="mt-3 play-btn"
                    fab
                    height="40px"
                    icon
                    width="40px"
                    @click.stop.prevent="toggleSongPlay(song)"
                  >
                    <v-icon v-show="!song.isPlaying">mdi-play</v-icon>
                    <v-icon v-show="song.isPlaying">mdi-pause</v-icon>
                  </v-btn>
                </div>
              </v-img>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
//get data from json file
// import SONGLIST from "../assets/data/tracklist.json";
// import SONGLIST from "../assets/data/songlist_test.json";
// import axios from "axios";
// const { distance } = require("fastest-levenshtein");
var myAudio = new Audio();
const axios = require("axios");
export default {
  components: {},
  name: "jobList",
  props: {
    showInput: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data() {
    return {
      baseUri: window.location.origin,
      // selectedPlaylist: "",
      searchText: "",
      songList: [],
      searchedsongList: [],
      selectedItem: {},
      dialog: false,
      color_assigned: "#8F36AA",
      mouseon_Album: {},
      currentPlaying: null,
      slotPosition: null,
    };
  },
  beforeCreate() {},
  created() {},
  mounted() {
    // this.localFetch();
    // this.fetchSongList();
    this.$emit("fetchSongList");
  },
  methods: {
    // localFetch() {
    //   // console.log(SONGLIST);
    //   let SONGLIST_json = JSON.parse(SONGLIST);
    //   this.songList = SONGLIST_json.map(function (item) {
    //     return {
    //       playlistName: item.playlistName,
    //       songId: item.id,
    //       songName: item.name,
    //       songTempo: item.tempo,
    //       artistName: item.artistName,
    //       preview_url: item.preview_url,
    //       img_url: item.img_url,
    //       release_date: item.release_date,
    //     };
    //   });
    //   // this.songList.sort(function (a, b) {
    //   //   return a.songName.toLowerCase().localeCompare(b.songName);
    //   // });
    //   // add other properties here such as hover on album cover
    //   for (let i = 0; i < this.songList.length; i++) {
    //     this.songList[i].hover_on_album = false;
    //     this.songList[i].isPlaying = false;
    //   }
    //   this.searchedsongList = this.songList;
    // },
    // async fetchSongList() {
    //   let arr = this.baseUri + "/requestTrackList";
    //   let SONGLIST = await axios.post(arr).then((response) => {
    //     return response.data;
    //   });
    //   console.log(SONGLIST);

    //   // console.log("Updated Tracklist fetched");

    //   let tracks = Object.values(SONGLIST.items);
    //   // console.log(tracks);
    //   this.songList = tracks.map(function (item) {
    //     return {
    //       playlistName: item.playlistName,
    //       songId: item.id,
    //       songName: item.name,
    //       songTempo: item.tempo,
    //       artistName: item.artist,
    //       preview_url: item.preview_url,
    //       img_url: item.img_url,
    //       release_date: item.release_date,
    //     };
    //   });
    //   // this.songList.sort(function (a, b) {
    //   //   return a.songName.toLowerCase().localeCompare(b.songName);
    //   // });
    //   // add other properties here such as hover on album cover
    //   for (let i = 0; i < this.songList.length; i++) {
    //     this.songList[i].hover_on_album = false;
    //     this.songList[i].isPlaying = false;
    //   }
    //   this.searchedsongList = this.songList;
    // },

    test() {
      // console.log(this.selectedItem);
    },
    mouseonAlbum(song) {
      // console.log("on album");
      song.hover_on_album = true; // to be deleted
      this.mouseon_Album = song;
    },
    mouseoffAlbum(song) {
      song.hover_on_album = false;
      // console.log("off album");
      this.mouseon_Album = {};
    },
    clearPlaylist() {
      let song = this.currentPlaying;
      myAudio.pause();
      song.isPlaying = false;
      this.currentPlaying = null;
    },
    toggleSongPlay(song) {
      if (song.isPlaying === false) {
        if (this.currentPlaying !== null) {
          this.clearPlaylist();
        }
        myAudio.src = song.preview_url;
        myAudio.play();
        myAudio.loop = true;
        this.currentPlaying = song;
        song.isPlaying = true;
      } else {
        // if (song.songId !== this.currentPlaying.songId) {
        //   console.log("not same song");
        //   return;
        // }
        myAudio.pause();
        song.isPlaying = false;
        this.clearPlaylist();
      }
      this.$forceUpdate();
    },
    searchSongs() {
      this.searchedsongList = this.songList;

      //return all result if there is no input entry
      if (this.searchText === "") {
        return this.searchedsongList;
      }
      //playlist has value -- this is from old version when there are two playlists, now it's only one library
      // if (this.selectedPlaylist !== "") {
      //   this.searchedsongList = this.searchedsongList.filter((song) => {
      //     return song.playlistName === this.selectedPlaylist;
      //   });
      // }

      //search text has value
      if (this.searchText !== "") {
        // let scoreList = [];
        // let searchText = this.searchText;
        // for (let i = 0; i < this.searchedsongList.length; i++) {
        //   let song = this.searchedsongList[i];
        //   console.log(song.songName);

        //   let compareText = song.songName + song.artistName;
        //   let text_distance = distance(searchText, compareText);
        //   let text_distance_obj = {
        //     songId: song.songId,
        //     distance: text_distance,
        //   };
        //   scoreList.push(text_distance_obj);
        //   console.log(text_distance);
        // }
        // scoreList.sort(function (a, b) {
        //   return a.distance - b.distance;
        // });

        // console.log(this.searchedsongList);

        this.searchedsongList = this.searchedsongList.filter((song) => {
          return (
            song.songName
              .toLocaleLowerCase()
              .indexOf(this.searchText.trim().toLocaleLowerCase()) > -1 || //for TR: to include ıöüşğİ
            song.artistName
              .toLocaleLowerCase()
              .indexOf(this.searchText.trim().toLocaleLowerCase()) > -1 || //for TR
            song.songName
              .toLowerCase()
              .indexOf(this.searchText.trim().toLowerCase()) > -1 || //general
            song.artistName
              .toLowerCase()
              .indexOf(this.searchText.trim().toLowerCase()) > -1
          ); //general
        });
      }

      // console.log("FILTERED COUNT: ",this.searchedsongList.length," TOTAL COUNT: ",this.songList.length,this.searchedsongList);
    },
    changeSongSelection(song) {
      this.selectedItem = {}; // clear all selectedItem
      // let add_song_order = Object.keys(this.selectedItem).length;
      this.selectedItem = Object.assign({}, this.selectedItem, {
        [song.songId]: song,
      });
      let added_song = this.selectedItem[song.songId];
      // added_song.isPlaying = false;
      added_song.color = this.color_assigned;
      added_song.class = `grid-item-song${this.slotPosition}`;
      this.$emit("changeSong", this.selectedItem);

      console.log("confirm add song in mb", song);
      var arr = this.baseUri + "/addSong";

      let userData = { url: String(song.songId) };
      axios.post(arr, userData).then(async (response) => {
        console.log("add response:", response);
        return String(response.data.task_id);
      });
    },
    toggleSongSelection(song) {
      if (this.selectedItem[song.songId]) {
        this.removeSelectedSong(song);
        return;
      }
      this.addSelectedSong(song);
      // console.log(this.selectedItem);
    },
    addSelectedSong(song) {
      if (Object.keys(this.selectedItem).length >= 4) {
        this.dialog = true;
        return;
      }
      // let add_song_order = Object.keys(this.selectedItem).length;
      this.selectedItem = Object.assign({}, this.selectedItem, {
        [song.songId]: song,
      });
      let added_song = this.selectedItem[song.songId];
      // added_song.isPlaying = false;
      added_song.color = this.color_assigned;
      added_song.class = `grid-item-song${this.slotPosition}`;
      this.$emit("songSelected", this.selectedItem);
    },
    removeSelectedSong(song) {
      delete this.selectedItem[song.songId];
      this.selectedItem = Object.assign({}, this.selectedItem);
      this.$emit("songSelected", this.selectedItem);
    },
  },

  computed: {
    // show all playlists' names
    filteredPlaylistNames() {
      let unique_array = [];
      for (let i = 0; i < this.songList.length; i++) {
        if (unique_array.indexOf(this.songList[i].playlistName) == -1) {
          unique_array.push(this.songList[i].playlistName);
        }
      }
      return unique_array;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1,
h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

.v-icon {
  margin-left: 2px;
  font-size: 18px;
}
/* .song-item {
  border: solid 1px lightgray;
  padding: 10px;
} */
.song-item:hover {
  background-color: #f3f3f3;
  opacity: 0.7;
  cursor: pointer;
}

.isSelected {
  background-color: #a3bce2;
}

/* .isSelected :hover {
  background-color: #a3bce2;
} */

input {
  width: 100%;
  padding: 12px 10px;
  margin: 8px 8px;
  box-sizing: border-box;
  outline-style: solid;
  border: 2px;
  color: whitesmoke;
}

input[type="text"]:focus {
  border: 3px solid #5e6f88;
  background-color: #a3bce2;
}

/* select {
  width: 100%;
  padding: 12px 20px;
  margin: 8px 0;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
} */

/* .songlist {
  max-height: 90%;
  overflow-y: auto;
}*/

/* .album_overlay {
  z-index: 9;
  height: 100%;
  background: whitesmoke;
  opacity: 0.3;
} */

v-img {
  z-index: 9;
}

/* .album_overlay:hover {
  height: 100%;
  background: whitesmoke;
  opacity: 0.5;
} */
.play-btn {
  opacity: 1;
  background-color: whitesmoke;
}

.container {
  background-color: white;
  /* background-color: #85d3eb; */
  /* animation: 1s infinite alternate ease-out breathing-color--dark; */
}

@keyframes breathing-color--dark {
  from {
    background-color: #85d3eb;
  }
  to {
    background-color: #05fec2;
  }
}

/* ===== Scrollbar CSS ===== */
/* Firefox */
* {
  scrollbar-width: auto;
  scrollbar-color: #00bffa #ffffff;
}

/* Chrome, Edge, and Safari */
*::-webkit-scrollbar {
  width: 12px;
}

*::-webkit-scrollbar-track {
  background: #ffffff;
}

*::-webkit-scrollbar-thumb {
  background-color: #00bffa;
  border-radius: 10px;
  border: 3px dashed #fafafa;
}
</style>
