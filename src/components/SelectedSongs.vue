<template>
  <v-container class="d-flex" style="padding-top: 0px; max-height: 9rem">
    <v-row dense>
      <v-col v-show="noItem">
        <div>
          <v-card color="secondary" light width="200px">
            <div class="d-flex flex-no-wrap justify-space-between">
              <div style="height: 100px; width: 200px; border-style: dashed">
                <v-card-text>
                  <div class="text-center">
                    <v-menu
                      v-model="menu"
                      :close-on-content-click="false"
                      absolute
                      :position-x="200"
                      :position-y="100"
                      offset-x
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-btn
                          class="mx-2"
                          color="white"
                          dark
                          fab
                          style="color: black"
                          v-bind="attrs"
                          v-on="on"
                          :isDisabled="preventAdd"
                        >
                          <v-icon dark> mdi-plus </v-icon>
                        </v-btn>
                      </template>
                      <div class="allLib">
                        <all-library
                          @changeSong="changeItem"
                          @toggleSpotifyOverlay="toggleOverlay"
                          @updateProgress="updateProgress"
                          @askColorAndSlot="assignColorAndSlot"
                          @updateDownloaded="updateDownloaded"
                          @fetchSongList="pushSongList"
                          @downloadFailed="downloadFailed"
                          ref="allLib"
                        ></all-library>
                      </div>
                    </v-menu>
                  </div>
                </v-card-text>
              </div>
            </div>
          </v-card>
        </div>
      </v-col>

      <v-col v-for="(item, i) in items" :key="i" cols="12">
        <div>
          <v-card
            :color="item.color"
            :draggable="draggable"
            class="droppable-element"
            dark
            hover
            unselectable="on"
            width="200px"
            max-height="140px"
            min-height="140px"
            @drag="drag(item)"
            @dragend="dragend(item)"
          >
            <v-btn v-show="deletable" icon @click.prevent="confirmDel(item)">
              <v-icon>mdi-trash-can</v-icon>
            </v-btn>
            <!-- <v-btn v-show="deletable" icon @click.prevent="menu = !menu">
              <v-icon>mdi-refresh</v-icon>
            </v-btn> -->
            <div class="d-flex flex-no-wrap justify-space-between">
              <div style="max-height: 130px">
                <v-card-title
                  class="text-body1"
                  style="font-size: medium !important"
                  v-text="item.songName"
                ></v-card-title>
                <v-card-subtitle
                  class="artist-name"
                  v-text="item.artistName"
                ></v-card-subtitle>
              </div>

              <v-avatar class="ma-3" size="60" tile>
                <v-img :src="item.img_url">
                  <v-card-actions>
                    <v-btn
                      v-show="item.preview_url !== null"
                      class="m-2"
                      fab
                      height="40px"
                      icon
                      right
                      width="40px"
                      @click.prevent="toggleSongPlay(item)"
                    >
                      <v-icon v-show="!item.isPlaying">mdi-play</v-icon>
                      <v-icon v-show="item.isPlaying">mdi-pause</v-icon>
                    </v-btn>

                    <!-- <v-btn
                    class="ml-2 mt-3"
                    fab
                    icon
                    height="40px"
                    right
                    width="40px"
                    @click.prevent="pauseSound(item)"
                  >
                    <v-icon>mdi-pause</v-icon>
                  </v-btn> -->
                  </v-card-actions>
                </v-img>
              </v-avatar>
            </div>

            <v-overlay :absolute="absolute" :value="spotifyOverlay">
              <v-btn
                color="success"
                :class="{ 'disable-events': disableCondition }"
                @click.prevent="fireSlot(item)"
              >
                {{ downloadMsg }}
                <!-- <v-progress-circular
                    indeterminate
                    color="white"
                    :size="28"
                    style="font-size: small; margin-left: 4px;"
                >{{ downloadProgress }}</v-progress-circular> -->
                <v-progress-circular
                  :rotate="360"
                  :size="28"
                  :width="5"
                  :value="downloadProgress"
                  color="white"
                  style="font-size: small; margin-left: 4px"
                >
                  {{ downloadProgress }}%
                </v-progress-circular>
              </v-btn>
            </v-overlay>
          </v-card>
        </div>
      </v-col>

      <v-dialog v-model="dialog" max-width="290" persistent>
        <v-card>
          <v-card-title class="text-h5">
            Are you sure you want to change the song?
          </v-card-title>
          <v-card-text
            >Upon confirmation, the layout of this song will be deleted.
            <v-checkbox
              v-model="neverShowMessage"
              label="Do not show this to me again"
            ></v-checkbox>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="green darken-1" text @click="cancel"> Cancel</v-btn>
            <v-btn color="green darken-1" text @click="confirm(itemToDel)">
              Confirm
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
  </v-container>
</template>

<script>
// import MiniLibrary from "./MiniLibrary.vue";
// import SpotifySearch from "./SpotifySearch.vue";
import AllLibrary from "./AllLibrary.vue";

var myAudio = new Audio();
export default {
  components: { AllLibrary },
  name: "selectedSongs",
  props: {
    draggable: { type: Boolean, required: false, default: true },
    deletable: { type: Boolean, required: false, default: true },
  },
  watch: {
    items(value) {
      if (value.length !== 0) {
        this.noItem = false;
      }
    },
    downloadProgress(value) {
      if (value != -1) {
        console.log("downloadProgress starting...");
      } else if (value == -1) {
        this.updateDownloaded();
      } else if (value == 100) {
        this.downloadProgress = -1;
      }
    },
  },
  data: () => ({
    downloadMsg: "Downloading",
    interval: {},
    downloadProgress: -1, //-1 means not downloading anything
    menu: false,
    noItem: true,
    userTempSelect: null,
    tab: null,
    preventAdd: false,
    disableCondition: true,
    items: [
      // {
      //   color: "#1F7087",
      //   img_url: "https://cdn.vuetifyjs.com/images/cards/foster.jpg",
      //   songName: "Supermodel",
      //   artistName: "Foster the People",
      //   isPlaying: false,
      // },
      // {
      //   color: "#952175",
      //   img_url: "https://cdn.vuetifyjs.com/images/cards/halcyon.png",
      //   songName: "Halcyon Days",
      //   artistName: "Ellie Goulding",
      //   isPlaying: false,
      // },
      // {
      //   color: "#1F7060",
      //   img_url: "https://cdn.vuetifyjs.com/images/cards/foster.jpg",
      //   songName: "Supermodel",
      //   artistName: "Foster the People",
      //   isPlaying: false,
      // },
      // {
      //   color: "#953287",
      //   img_url: "https://cdn.vuetifyjs.com/images/cards/halcyon.png",
      //   songName: "Halcyon Days",
      //   artistName: "Ellie Goulding",
      //   isPlaying: false,
      // },
    ],
    dialog: false, //confirm if user really want to change the song
    currentPlaying: null,
    situation: null, // 0 is delete, 1 is add the song and 2 is change the song
    absolute: true,
    spotifyOverlay: false,
    neverShowMessage: false,
    color: null,
    slotPosition: null,
    songList: [],
  }),
  beforeCreate() {},
  created() {},
  mounted() {
    // console.log("selectedSongs.vue is mounted");
    this.$emit("fetchSongList");

    this.interval = setInterval(() => {
      if (this.downloadProgress == 100) {
        return (this.downloadProgress = -1);
      }
    }, 2000);
  },
  beforeDestroy() {
    clearInterval(this.interval);
  },
  methods: {
    test() {
      // console.log(this.items);
    },
    // addSelectedSong(item) {
    //   console.log("Adding song:", item);
    //   this.items.push(item);
    // },
    pushSongList() {
      //send songlist to allLib -> minilibrary.vue and spotifySearch.vue
      this.$refs.allLib.$refs.miniLibrary.searchedsongList = this.songList;
      // console.log("Finish pushing to minilibrary searchedSongs");
      this.$refs.allLib.$refs.miniLibrary.songList = this.songList;
      // console.log("Finish pushing to minilibrary songList");
      this.$refs.allLib.$refs.spotifySearch.savedsongList = this.songList;
      // console.log("Finish pushing to spotify savedSongList");
    },
    updateDownloaded() {
      this.$emit("updateDownloaded");
    },
    drag(item) {
      this.$emit("dragging", item);
      // console.log("dragging:", item);
    },
    dragend(item) {
      this.$emit("dragend", item);
    },
    confirmDel(item) {
      console.log("confirmDel item is:", item);
      this.itemToDel = item;
      this.situation = 0;
      this.confirm(item);
      // if (this.neverShowMessage == true)
      //   this.confirm(item);
      // } else {
      //   // this.dialog = true;
      // }
    },
    del() {
      // this.$delete(this.items, index);
      this.userTempSelect = null;
      let key = this.itemToDel.songId;
      delete this.items[key];
      this.noItem = true;
    },
    playSound(item) {
      if (this.items) {
        for (let i = 0; i < this.items.length; i++) {
          this.items[i].isPlaying = false;
        }
      }
      this.currentPlaying = null;
      myAudio.src = item.preview_url;
      myAudio.play();
      item.isPlaying = true;
      myAudio.loop = true;
      this.currentPlaying = item;
    },
    pauseSound(item) {
      if (item.songId !== this.currentPlaying.songId) {
        return;
      }
      myAudio.pause();
      item.isPlaying = false;
    },
    changeItem(selectedItem) {
      console.log("change item:", selectedItem);
      this.menu = false;
      let currentSongId = Object.keys(this.items)[0];
      //if selectedItem is the same song, or previous song is null, return
      if (currentSongId === Object.keys(selectedItem)[0]) {
        // console.log("choosing the same song");
        return;
      }
      this.userTempSelect = selectedItem;
      this.situation = 1;
      this.confirm(selectedItem);
      //if there is content in layout, confirm the change. If not, change directly.
      // if (this.neverShowMessage == true) {
      //   this.confirm(selectedItem);
      // } else if (this.noItem == true) {
      //   this.confirm(selectedItem);
      // } else {
      //   this.dialog = true;
      // }
    },
    confirm(item) {
      // console.log("confirm:", item, "\t situation:", this.situation);
      //once confirm
      this.dialog = false; //close the warning dialog
      if (this.neverShowMessage == true) {
        // If user choose not to show the warning message again, send an info to clip board and change all selected songs components' dialog to false
        this.$emit("noDelWarning");
      }
      let currentSongId = Object.keys(this.items)[0];
      if (this.situation === 1) {
        this.$emit("confirmAddSong", item);
        this.items = this.userTempSelect; //after confirmation, change the song
      } else if (this.situation === 0) {
        this.$emit("confirmDeleteSong", item); //send a message to clipboard then to Mixboard to delete song in the layout
        console.log("confirmDeleteSong", item);
        this.del();
      } else if (this.situation === 2) {
        this.$emit("confirmDeleteSong", currentSongId);
        console.log("current song to del:", this.items[currentSongId]);
        this.itemToDel = this.items[currentSongId];
        this.del();
        this.$emit("confirmAddSong", item); //send a message to Mixboard to delete the song in layout, but here it can only send to clipboard first
        this.items = item;
      }
      this.$emit("updateYourSlotItem");
    },
    cancel() {
      this.userTempSelect = null;
      this.itemToDel = null;
      this.situation = null;
      this.dialog = false;
    },
    // toggleSoundPlay(item) {
    //   // let id = item.songId;
    //   // console.log(this.items[id]);

    //   if (!myAudio.paused) {
    //     myAudio.pause();
    //     for (let i = 0; i < this.items.length; i++) {
    //       this.items[i].isPlaying = false;
    //     }
    //   } else {
    //     myAudio.src = item.preview_url;
    //     myAudio.play();
    //     item.isPlaying = true;
    //     myAudio.loop = true;
    //   }
    // },
    toggleSongPlay(item) {
      if (item.isPlaying === false) {
        for (let i = 0; i < this.items.length; i++) {
          this.items[i].isPlaying = false;
        }
        myAudio.src = item.preview_url;
        myAudio.play();
        myAudio.loop = true;
        this.currentPlaying = item;
        // console.log(this.currentPlaying);
        item.isPlaying = true;
      } else {
        // console.log(this.currentPlaying);
        // if (item.songId !== this.currentPlaying.songId) {
        //   return;
        // }
        myAudio.pause();
        item.isPlaying = false;
        this.currentPlaying = null;
      }
      this.$forceUpdate();
    },
    toggleOverlay() {
      this.spotifyOverlay = !this.spotifyOverlay;
      if (!this.spotifyOverlay) {
        // if close overlay, reset the downloadProgress to -1
        this.downloadProgress = -1;
      }
    },
    updateProgress(value) {
      this.downloadProgress = value;
    },
    assignColorAndSlot() {
      this.$refs.allLib.color_assigned = this.color;
      this.$refs.allLib.slotPosition = this.slotPosition;
    },
    downloadFailed() {
      console.log("download Failed!");
      this.downloadMsg = "Fail, click to close";
      this.disableCondition = false;
    },
    fireSlot(item) {
      this.toggleOverlay();
      this.confirmDel(item);
      this.disableCondition = true;
    },
  },
};
</script>

<style scoped>
.flexcard {
  display: flex;
  flex-direction: column;
}

.text-body1 {
  font-size: 0.8vw;
  width: 70%;
  text-overflow: clip;
  overflow: hidden;
  position: absolute;
  white-space: nowrap;
  transform: translateX(0);
  transition: 5s;
}

.text-body1:hover {
  width: auto;
  transform: translateX(-80%);
}

.artist-name {
  margin-top: 70px !important;
}

.droppable-element {
  cursor: move !important;
}

.v-progress-circular {
  /*margin: 1rem;*/
}

.artist-name {
  margin-top: 60px !important;
}

.disable-events {
  pointer-events: none;
}
</style>
