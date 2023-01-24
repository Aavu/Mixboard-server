<template>
  <v-container>
    <v-row dense justify="space-around" no-gutters>
      <v-card max-width="auto" min-width="250px">
        <v-app-bar color="#7f91bc" flat class="">
          <v-toolbar-title class="" style="color: #f8f8ff; width: auto">
            <span class="title noselect" style="margin-left: 1rem"
              >1. Select Songs</span
            >
            <v-btn
              fab
              small
              color="primary"
              :disabled="randomDisabled"
              @click="selectRandomSongs"
              style="margin-left: 1rem"
              ><v-icon title="random selection"
                >mdi-dice-3-outline</v-icon
              ></v-btn
            >
          </v-toolbar-title>
        </v-app-bar>

        <v-card-text>
          <!-- <v-overlay :absolute="absolute" :value="overlay">
            <mini-library @changeSong="changeSong"></mini-library>
            <v-btn color="success" @click="overlay = false">
              Hide Overlay
            </v-btn>
          </v-overlay> -->
          <div>
            <!-- <v-btn @click="test">test</v-btn> -->
            <div v-for="slot in slots" :key="slot.key">
              <selected-songs
                :ref="slot.ref"
                :deletable="deletableSlot"
                @confirmSongChange="confirmSongChange"
                @confirmDeleteSong="confirmDeleteSong"
                @confirmAddSong="confirmAddSong"
                @dragend="dragend"
                @dragging="drag"
                @updateYourSlotItem="changeSlotItem(slot)"
                @noDelWarning="closeAllWarnings"
                @updateDownloaded="updateDownloaded"
                @fetchSongList="fetchSongList"
                @selectRandomSong="$emit('selectRandomSong')"
              ></selected-songs>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-row>
  </v-container>
</template>

<script>
// import JobList from "./JobList.vue";
import SelectedSongs from "./SelectedSongs.vue";
// import SONGLIST from "../assets/data/songlist_test.json";
import axios from "axios";

export default {
  components: { SelectedSongs },
  data: () => ({
    dialog: false,
    overlay: false,
    absolute: true,
    deletableSlot: true,
    randomDisabled: false,
    slots: [
      //each item is an object with key value pairs; key is the songId, value is songObject
      { ref: "selectedSongs0", key: "slot0", item: null, color: null },
      { ref: "selectedSongs1", key: "slot1", item: null, color: null },
      { ref: "selectedSongs2", key: "slot2", item: null, color: null },
      { ref: "selectedSongs3", key: "slot3", item: null, color: null },
    ], //four empty slots
    baseUri: window.location.origin,
    songList: [],
    // searchedSongList: [],
  }),
  created() {},
  watch: {},
  methods: {
    test() {
      console.log(this.$refs.selectedSongs0);
      for (let i = 0; i < this.slots.length; i++) {
        let refName = this.slots[i].ref;
        console.log(refName);
        console.log(this.$refs[refName]);
      }
    },
    updateDownloaded() {
      // console.log("updateDownloaded");
      this.$emit("updateDownloaded");
      this.fetchSongList(); //once spotify downloaded is done, SpotifySearch.vue send message -> AllLibrary.vue->SelectedSongs->Clipboard.vue
    },
    drag(item) {
      this.$emit("dragging", item); //from selectedSongs.vue
    },
    dragend(item) {
      this.$emit("dragend", item); //from selectedSongs.vue
    },
    // showSelected() {
    //   this.dialog = !this.dialog;
    //   this.$refs.selectedSongs.items = this.$refs.jobList.selectedItem;
    //   // console.log(this.$refs.selectedSongs.items);
    // },
    changeSlotItem(slot) {
      console.log(slot);
      console.log("changeSlotItem!", this.$refs[slot.ref]);
      slot.item = this.$refs[slot.ref][0].items;
      console.log(slot.item);
      //update this.slots as well
      console.log(this.slots);
    },
    confirmSongChange(song) {
      // console.log("confirmSongChange clipboard", song);
      this.$emit("confirmSongChange", song);
    },
    confirmDeleteSong(song) {
      this.$emit("confirmDeleteSong", song);
    },
    confirmAddSong(song) {
      this.$emit("confirmAddSong", song);
    },
    selectRandomSongs() {
      this.$emit("randomSongs");
      let downloadedSongs = this.songList;
      var selectedItem;
      let randomIndexList = [];
      for (let i = 0; i < this.slots.length; i++) {
        let refName = this.slots[i].ref;
        let ref_slot = this.$refs[refName][0];
        //if the slot is downloading, skip
        if (ref_slot.spotifyOverlay) {
          continue;
        }
        let random_index = Math.floor(Math.random() * downloadedSongs.length);
        //check if the same song has been selected, if downloaded song length is less than slots number, then allow duplication
        while (
          downloadedSongs.length >= this.slots.length &&
          randomIndexList.includes(random_index)
        ) {
          // console.log("same index included", randomIndexList, random_index);
          random_index = Math.floor(Math.random() * downloadedSongs.length);
        }
        randomIndexList.push(random_index);
        let random_song = downloadedSongs[random_index];
        //select a random song from the internal library fetched on refresh

        for (let item_key in ref_slot.items) {
          // console.log(`check slot item: ${item_key}`);
          let item = ref_slot.items[item_key];
          ref_slot.confirmDel(item);
        }
        ref_slot.items = []; // clear all items in selectedSongs.vue
        selectedItem = {};
        selectedItem = Object.assign({}, selectedItem, {
          [random_song.songId]: random_song,
        });
        let added_song = selectedItem[random_song.songId];
        added_song.color = ref_slot.color;
        added_song.class = `grid-item-song${ref_slot.slotPosition}`;
        ref_slot.changeItem(selectedItem); //call changeItem function in the SelectedSongs.vue

        console.log("confirm add song in mb", random_song);
        var arr = this.baseUri + "/addSong";

        let userData = { url: String(random_song.songId) };
        axios.post(arr, userData).then(async (response) => {
          console.log("add response:", response);
          return String(response.data.task_id);
        });
      }
    },
    closeAllWarnings() {
      for (let i = 0; i < this.slots.length; i++) {
        let slot = this.slots[i];
        let slot_ref = slot.ref;
        this.$refs[slot_ref][0].neverShowMessage = true;
      }
    },
    async fetchSongList() {
      //fetch song list everytime the page is mounted
      let arr = this.baseUri + "/requestTrackList";
      console.log("clipboard is requesting Tracklist...");
      let SONGLIST = await axios.post(arr).then((response) => {
        return response.data;
      });
      // console.log(SONGLIST);
      let tracks = Object.values(SONGLIST.items);
      // console.log(tracks);
      let songList = tracks.map(function (item) {
        return {
          playlistName: item.playlistName,
          songId: item.id,
          songName: item.name,
          songTempo: item.tempo,
          artistName: item.artist,
          preview_url: item.preview_url,
          img_url: item.img_url,
          release_date: item.release_date,
        };
      });
      // add other properties here such as hover on album cover
      for (let i = 0; i < this.songList.length; i++) {
        songList[i].hover_on_album = false;
        songList[i].isPlaying = false;
      }
      this.songList = songList;
      //send songList to selectedSongs.vue
      this.pushSongList();
    },
    pushSongList() {
      for (let i = 0; i < this.slots.length; i++) {
        let refName = this.slots[i].ref;
        this.$refs[refName][0].songList = this.songList;
      }
    },
  },

  // confirmDeleteSong(song) {
  //   this.$emit("confirmDeleteSong", song);
  // },
  // confirmAddSong(song) {
  //   this.$emit("confirmAddSong", song);
  // },
  mounted() {
    this.fetchSongList();
  },
};
</script>

<style scoped>
.title {
  font-size: 20px;
  font-family: "Fantasy";
}
.dialog {
  min-height: 500px;
}

.noselect {
  -webkit-touch-callout: none; /* iOS Safari */
  -webkit-user-select: none; /* Safari */
  -khtml-user-select: none; /* Konqueror HTML */
  -moz-user-select: none; /* Old versions of Firefox */
  -ms-user-select: none; /* Internet Explorer/Edge */
  user-select: none;
  /* Non-prefixed version, currently
                                   supported by Chrome, Edge, Opera and Firefox */
}
</style>
