<template>
  <div>
    <div class="container">
      <div>
        <v-row align="baseline" style="margin-bottom: 4px" v-show="showInput">
          <input
            v-show="showInput"
            v-model="searchText"
            placeholder="Song/Artist"
            style="color: #33101c"
            type="text"
            @keyup="getSearchResult()"
          />
        </v-row>
      </div>
      <div
        style="
          max-width: 100%;
          max-height: 100%;
          overflow-y: hidden;
          overflow-x: hidden;
        "
      >
        <div
          v-for="song in searchedSonglist"
          :key="song.id"
          :class="{ isSelected: selectedItem[song.id] }"
          class="searchResult my-3"
          style="
            max-height: 200px;
            max-width: 100%;
            overflow: hidden;
            border-bottom: 1px solid grey;
          "
          @click="changeSongSelectionWrapper(song)"
        >
          <div class="row song-item">
            <div class="col-sm-6" style="text-transform: capitalize">
              <span>{{ song.name }}</span>
              <br />
              <span class="font-weight-light text-muted"
                >{{ song.artists[0].name
                }}<v-icon v-show="song.isDownloaded" color="#77eb34"
                  >mdi-check-underline</v-icon
                ><v-icon v-show="!song.isDownloaded"
                  >mdi-cloud-download</v-icon
                ></span
              ><v-icon v-show="!song.isDownloaded" color="#1db954"
                >mdi-spotify</v-icon
              >
            </div>

            <div class="col-sm-5 col-xs-5 text-center">
              <v-img
                :src="song.album.images[0].url"
                alt="image"
                blank-color="#ccc"
                style="height: auto"
              >
                <div class="album_overlay">
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
var myAudio = new Audio();
const axios = require("axios");
const qs = require("qs");
require("dotenv").config();
const client_id = process.env.VUE_APP_SPOTIFY_API_ID; // Your client id
const client_secret = process.env.VUE_APP_SPOTIFY_CLIENT_SECRET; // Your secret
const auth_token = Buffer.from(
  `${client_id}:${client_secret}`,
  "utf-8"
).toString("base64");
let host =
  window.location.protocol +
  "//" +
  window.location.hostname +
  ":" +
  window.location.port;
export default {
  components: {},
  props: {
    showInput: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  watch: {
    savedsongList() {
      console.log("savedSongList has been updated!");
      this.$emit("updateDownloaded");
    },
  },
  data: () => ({
    baseUri: host,
    inputs: [],
    searchText: "",
    searchedSonglist: [],
    songList: [],
    selectedItem: {},
    dialog: false,
    color_assigned: "#8F36AA",
    mouseon_Album: {},
    currentPlaying: null,
    savedsongList: [],
    slotPosition: null,
  }),
  beforeMount() {
    // console.log("setting up");
    this.getDefaultRecommendations();
  },
  methods: {
    test() {
      // console.log(this.getSearchResult("talk it up"));
    },
    // async fetchSongList() {
    //   let arr = this.baseUri + "/requestTrackList";
    //   let SONGLIST = await axios.post(arr).then((response) => {
    //     // console.log(response.status);
    //     console.log("fetched Song list:", response.data);
    //     return response.data;
    //   });

    //   let tracks = Object.values(SONGLIST.items);
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
    //   this.savedsongList = this.songList;
    // },
    async getAuth() {
      try {
        //make post request to SPOTIFY API for access token, sending relavent info
        const token_url = "https://accounts.spotify.com/api/token";
        const data = qs.stringify({ grant_type: "client_credentials" });

        const response = await axios.post(token_url, data, {
          headers: {
            Authorization: `Basic ${auth_token}`,
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });
        //return access token
        return response.data.access_token;
        //console.log(response.data.access_token);
      } catch (error) {
        //on fail, log the error in console
        console.log(error);
      }
    },

    async getAudioFeatures_Track(track_id) {
      //request token using getAuth() function
      let access_token = await this.getAuth();
      //console.log(access_token);

      let api_url = `https://api.spotify.com/v1/tracks/${track_id}`;
      //console.log(api_url);
      try {
        const response = await axios.get(api_url, {
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        });
        //console.log(response.data);
        return response.data;
      } catch (error) {
        console.log(error);
      }
    },
    async getDefaultRecommendations() {
      let access_token = await this.getAuth();
      let api_url =
        "https://api.spotify.com/v1/recommendations?limit=20&seed_genres=pop";
      try {
        await axios
          .get(api_url, {
            headers: {
              Authorization: `Bearer ${access_token}`,
            },
          })
          .then((response) => {
            console.log(response);
            let items = response.data.tracks;
            for (let i = 0; i < items.length; i++) {
              items[i].isPlaying = false;
              //check if searchedSong is already downloaded
              items[i].isDownloaded = this.checkIsDownloaded(items[i].id);
            }
            this.searchedSonglist = items;

            // //adjust the bottom menu position
            // this.$emit("getDefaultRecommendations");
          });
      } catch (error) {
        console.log(error);
      }
    },
    async getSearchResult() {
      let search_word = this.searchText;
      //request token using getAuth() function
      let access_token = await this.getAuth();
      //console.log(access_token);

      let api_url = `https://api.spotify.com/v1/search?q=${search_word}&type=track%2Cartist`;
      //console.log(api_url);
      try {
        await axios
          .get(api_url, {
            headers: {
              Authorization: `Bearer ${access_token}`,
            },
          })
          .then((response) => {
            let items = response.data.tracks.items;
            for (let i = 0; i < items.length; i++) {
              items[i].isPlaying = false;
              //check if searchedSong is already downloaded
              items[i].isDownloaded = this.checkIsDownloaded(items[i].id);
            }
            this.searchedSonglist = items;
          });

        // console.log(this.searchedSonglist);
        // this.$forceUpdate();
        // return response.data;
      } catch (error) {
        console.log(error);
      }
    },
    checkIsDownloaded(songId) {
      for (let i = 0; i < this.savedsongList.length; i++) {
        let song = this.savedsongList[i];
        if (song.songId == songId) {
          return true;
        }
      }
      return false;
    },
    // showSearchResult(search_word) {
    //   let data = this.getSearchResult(search_word);
    //   let items = data.tracks.items;
    //   let access_token = this.getAuth();
    //   //get all tracks info
    //   for (let i = 0; i < items.length; i++) {
    //     let id = items[i].id;
    //     let api_url = `https://api.spotify.com/v1/tracks/${id}`;
    //     try {
    //       const track_info = await axios
    //         .get(api_url, {
    //           headers: {
    //             Authorization: `Bearer ${access_token}`,
    //           },
    //         })
    //         .then((response) => {
    //           console.log(response);
    //         });
    //       console.log(track_info);
    //       //console.log(response.data);
    //     } catch (error) {
    //       console.log(error);
    //     }
    //   }
    //   this.searchedSonglist = data.tracks.items;
    // },
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
        myAudio.pause();
        song.isPlaying = false;
        this.clearPlaylist();
      }
      this.$forceUpdate();
    },

    changeSongSelection(song) {
      this.selectedItem = {}; // clear all selectedItem
      // let add_song_order = Object.keys(this.selectedItem).length;
      this.selectedItem = Object.assign({}, this.selectedItem, {
        [song.id]: {
          playlistName: song.playlistName,
          songId: song.id,
          songName: song.name,
          songTempo: song.tempo,
          artistName: song.artists[0].name,
          preview_url: song.preview_url,
          img_url: song.album.images[0].url,
          release_date: song.album.release_date,
        },
      });
      // console.log("selected Item is:", this.selectedItem);
      // let added_song = this.selectedItem[song.id];
      // added_song.isPlaying = false;
      this.selectedItem[song.id].color = this.color_assigned;
      this.selectedItem[song.id].class = `grid-item-song${this.slotPosition}`;
      this.$emit("changeSong", this.selectedItem); //send message -> AllLibrary.vue -> selectedsongs.vue changeItem-> mixboard.vue confirmAddSong
    },
    async changeSongSelectionWrapper(track) {
      // await this.fetchSongList();
      //check if the song is already downloaded
      for (const element of this.savedsongList) {
        if (element.id === track.id) {
          console.log("song is already downloaded!");
          return this.changeSongSelection(element);
        }
      }
      this.changeSongSelection(track);

      // if the song has not been downloaded, see if another song is downloading
      this.$emit("toggleSpotifyOverlay"); //add overlay
      this.$emit("updateProgress", 0);
      // let arr = this.baseUri + "/requestSpotify";
      // let userData = { url: track.external_urls.spotify };
      // let taskID = await axios.post(arr, userData).then(async (response) => {
      //   return String(response.data.task_id);
      // });

      console.log("confirm add song in mb", track);
      var arr = this.baseUri + "/addSong";

      let userData = { url: String(track.id) };
      axios
        .post(arr, userData)
        .then(async (response) => {
          console.log("add response:", response);
          // trigger updatestatus(taskID)
          // console.log("download song taskID is:", String(response.data.task_id));
          let taskID = String(response.data.task_id);
          await this.updateStatus(taskID);
          this.$emit("updateDownloaded");
          console.log("updateDownloaded Message sent!");
          return String(response.data.task_id);
        })
        .catch((err) => {
          this.$emit("downloadFailed");
          console.log(err);
        });

      // await this.fetchSongList();
    },
    async updateStatus(taskID) {
      console.log("status spotify:", taskID);
      let pollingResponse = await this.getTaskStatus(taskID);
      // console.log("Operation status is " + pollingResponse.task_status);
      console.log("pollingResponse", pollingResponse);
      while (pollingResponse.requestStatus !== "SUCCESS") {
        if (pollingResponse.requestStatus === "FAILURE") {
          alert("Download failed, please try again!");
          return;
        }
        pollingResponse = await this.getTaskStatus(taskID);
        console.log("pollingResponse", pollingResponse);
        if (pollingResponse.requestStatus === "PROGRESS") {
          this.$emit("updateProgress", pollingResponse.task_result.progress);
        }
      }

      // console.log("Operation status is " + pollingResponse.task_status);
      this.$emit("toggleSpotifyOverlay");
    },
    toggleSongSelection(song) {
      if (this.selectedItem[song.id]) {
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
      let add_song_order = Object.keys(this.selectedItem).length;
      this.selectedItem = Object.assign({}, this.selectedItem, {
        [song.id]: song,
      });
      let added_song = this.selectedItem[song.id];
      // added_song.isPlaying = false;
      added_song.color = this.color_assigned;
      added_song.class = `grid-item-song${add_song_order}`;
      this.$emit("songSelected", this.selectedItem);
    },
    removeSelectedSong(song) {
      delete this.selectedItem[song.id];
      this.selectedItem = Object.assign({}, this.selectedItem);
      this.$emit("songRemoved", this.selectedItem);
    },
    // async fetchResult(taskID, baseUri) {
    //   let fetchURI = baseUri + "/requestResult/" + taskID;

    //   let res = await axios
    //     .post(fetchURI)
    //     .then(function (response) {
    //       return response.data.task_result;
    //     })
    //     .catch((err) => {
    //       console.error(err);
    //     });

    //   return res;
    // },
    async getTaskStatus(taskID) {
      let taskStatusURI = this.baseUri + "/requestStatus/" + taskID;
      console.log(taskStatusURI);
      let res = await axios
        .get(taskStatusURI)
        .then(function (response) {
          console.log("spotify response:", response);
          return response.data;
        })
        .catch((err) => {
          console.error(err);
        });
      return res;
    },
  },
};
</script>

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
  border: 3px solid #5e8868;
  background-color: #a3e2b7;
}

v-img {
  z-index: 9;
}

.play-btn {
  opacity: 1;
  background-color: whitesmoke;
}
.container {
  background-color: white;
  margin-right: 0px;
  padding: 0px;
  /* background-color: #9dd392;
  animation: 1s infinite alternate ease-out breathing-color--dark;
  animation-duration: 1s; */
}
@keyframes breathing-color--dark {
  from {
    background-color: yellow;
  }
  to {
    background-color: #05fec2;
  }
}

/* ===== Scrollbar CSS ===== */
/* Firefox */
* {
  scrollbar-width: auto;
  scrollbar-color: #9dd392 #ffffff;
}

/* Chrome, Edge, and Safari */
*::-webkit-scrollbar {
  width: 12px;
}

*::-webkit-scrollbar-track {
  background: #ffffff;
}

*::-webkit-scrollbar-thumb {
  background-color: #9dd392;
  border-radius: 10px;
  border: 3px dashed #fafafa;
}
</style>
