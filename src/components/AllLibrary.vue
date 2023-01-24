<template>
  <div>
    <div
      class="container"
      style="overflow: scroll; background-color: white; padding-right: 1px"
    >
      <div style="max-width: 240px; max-height: 500px">
        <div>
          <input
            style="color: #33101c"
            v-model="searchText"
            placeholder="Song/Artist"
            type="text"
            @keyup="search"
          />
          <v-btn fab small color="primary" @click="selectRandomSong"
            ><v-icon title="random selection">mdi-dice-3-outline</v-icon></v-btn
          >
        </div>
        <!-- <v-btn-toggle v-model="libraryToggle" rounded style="margin: 2px"
          ><v-btn small title="only show prepared songs"
            >Downloaded</v-btn
          ></v-btn-toggle
        > -->
        <!-- <v-checkbox v-model="showMini" :label="`downloaded`"></v-checkbox>
        <v-checkbox v-model="showSpotify" :label="`Cloud`"></v-checkbox> -->

        <mini-library
          v-show="false"
          ref="miniLibrary"
          @changeSong="changeSong"
          @fetchSongList="fetchSongList"
          :showInput="false"
        ></mini-library>
        <spotify-search
          v-show="showSpotify"
          :showInput="false"
          ref="spotifySearch"
          @changeSong="changeSong"
          @toggleSpotifyOverlay="toggleSpotifyOverlay"
          @updateProgress="updateProgress"
          @updateDownloaded="updateDownloaded"
          @downloadFailed="downloadFailed"
        ></spotify-search>
      </div>
    </div>
  </div>
</template>

<script>
import MiniLibrary from "./MiniLibrary.vue";
import SpotifySearch from "./SpotifySearch.vue";
// import DiceD6 from "vue-dice-d6";
export default {
  components: { MiniLibrary, SpotifySearch },
  name: "allLibrary",
  props: {},
  data() {
    return {
      searchText: "",
      // showMini: true,
      showSpotify: true,
      color_assigned: null,
      result: 1,
      start: false,
      libraryToggle: null,
    };
  },
  mounted() {
    this.$emit("askColorAndSlot");
    this.$refs.miniLibrary.color_assigned = this.color_assigned;
    this.$refs.miniLibrary.slotPosition = this.slotPosition;
    this.$refs.spotifySearch.color_assigned = this.color_assigned;
    this.$refs.spotifySearch.slotPosition = this.slotPosition;
  },
  watch: {
    libraryToggle(value) {
      console.log(value);
      if (value == 0) {
        this.showSpotify = false;
      } else {
        this.showSpotify = true;
      }
    },
  },
  methods: {
    fetchSongList() {
      this.$emit("fetchSongList"); //ask SelectedSongs for songList
    },
    search() {
      this.$refs.miniLibrary.searchText = this.searchText;
      this.$refs.miniLibrary.searchSongs();
      this.$refs.spotifySearch.searchText = this.searchText;
      this.$refs.spotifySearch.getSearchResult();
    },
    changeSong(selectedItem) {
      this.$emit("changeSong", selectedItem);
    },
    toggleSpotifyOverlay() {
      this.$emit("toggleSpotifyOverlay");
    },
    updateProgress(value) {
      console.log("update Progress", value);
      this.$emit("updateProgress", value); //fix the bug of sending 0
    },
    updateDownloaded() {
      this.$emit("updateDownloaded");
    },
    selectRandomSong() {
      this.$emit("selectRandomSong");
      //select a random song from the internal library
      let downloadedSongs = this.$refs.miniLibrary.searchedsongList;
      let random_index = Math.floor(Math.random() * downloadedSongs.length);
      let random_song = downloadedSongs[random_index];
      this.$refs.miniLibrary.changeSongSelection(random_song);
    },
    toggleResult() {
      // if dice is animating
      if (this.start) {
        // use setTimeout for stopped transition
        setTimeout(() => {
          this.result = Math.ceil(Math.random() * 6);
        });
      }
      this.start = !this.start;
    },
    downloadFailed() {
      this.$emit("downloadFailed");
    },
  },
};
</script>

<style scoped>
input {
  width: 75%;
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
  background-color: white;
  border-radius: 10px;
  border: 3px double #fafafa;
}

.dice-wrapper {
  width: 100px;
  height: 100px;
}
</style>
