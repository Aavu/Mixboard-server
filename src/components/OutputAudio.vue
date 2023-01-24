<template>
  <div class="text-center pt-0">
    <!-- <v-btn @click="test">test</v-btn> -->
    <!-- <v-menu
      v-model="player"
      :close-on-content-click="false"
      offset-x
      transition="scale-transition"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-badge color="red" :content="badge" :value="badge" overlap
          ><v-btn color="primary" dark fab v-bind="attrs" v-on="on">
            <icon>mdi-music</icon>
          </v-btn></v-badge
        >
      </template> -->
    <v-card class="pa-0" flat>
      <v-layout align="center" justify="center" no-gutters row wrap>
        <v-flex lg4 md4 xs2>
          <v-list>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title v-if="currentAudio"
                  >{{ currentAudio.audioName }}
                </v-list-item-title>
                <!-- <v-list-item-subtitle>{{ userName }}</v-list-item-subtitle> -->
              </v-list-item-content>
              <!-- <v-list-item-icon>
              <v-btn icon @click="previousSong">
                <v-icon>mdi-rewind</v-icon>
              </v-btn>
            </v-list-item-icon> -->

              <v-list-item-icon>
                <v-btn
                  style="background-color: #f4f4f4"
                  icon
                  @click="toggleSongPlay"
                  :disabled="isDisabled"
                >
                  <v-icon large v-show="!isPlaying">mdi-play</v-icon>
                  <v-icon large v-show="isPlaying">mdi-pause</v-icon>
                </v-btn>
              </v-list-item-icon>

              <!-- <v-list-item-icon
              class="ml-0"
              :class="{ 'mr-3': $vuetify.breakpoint.mdAndUp }"
            >
              <v-btn icon @click="nextSong">
                <v-icon>mdi-fast-forward</v-icon>
              </v-btn>
            </v-list-item-icon> -->
            </v-list-item>
          </v-list>
        </v-flex>
        <v-flex lg8 md8 xs10>
          <v-slider
            v-model="position"
            always-dirty
            class="mt-3 pt-3"
            color="#7f91bc"
            hide-details
            max="1000"
            min="0"
            track-color="grey"
            @change="dragSlider"
          >
            <!-- <template v-slot:prepend> -->
            <!-- <v-icon color="primary"> mdi-minus </v-icon> -->
            <!-- </template> -->
            <template v-slot:append>
              <v-menu
                v-model="menu"
                :close-on-content-click="false"
                origin="center center"
                top
                transition="scale-transition"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    class="mx-2"
                    color="#7f91bc"
                    fab
                    small
                    v-bind="attrs"
                    @click="clearBadge"
                    v-on="on"
                    :disabled="isPlaying"
                  >
                    <v-badge :content="badge" :value="badge" overlap>
                      <v-icon
                        color="white"
                        title="check your history mashup here"
                      >
                        mdi-playlist-music</v-icon
                      >
                    </v-badge>
                  </v-btn>
                </template>
                <v-card class="mx-auto" max-width="500" tile>
                  <v-list>
                    <v-list-item-group v-model="selectedItem" color="primary">
                      <v-list-item
                        v-for="(item, i) in items"
                        :id="item.audioId"
                        :key="i"
                        :disabled="lockSelection"
                      >
                        <v-list-item-content>
                          <v-list-item-title
                            >{{ item.audioName }}
                          </v-list-item-title>
                          <v-list-item-subtitle
                            >{{ item.timeStamp }}
                          </v-list-item-subtitle>
                        </v-list-item-content>
                        <v-list-item-action>
                          <v-row>
                            <v-btn icon
                              ><a
                                :id="item.downloadId"
                                :download="item.audioName"
                                :href="item.audioSrc"
                              >
                                <v-icon color="grey lighten-1"
                                  >mdi-download
                                </v-icon>
                              </a></v-btn
                            >
                            <edit-name
                              ref="editName"
                              @saveEdit="editName(item, $event)"
                              @getAudioName="
                                sendAudioName(item.audioName, item.audioId)
                              "
                            ></edit-name>

                            <v-btn icon @click.prevent="removeAudio(item)">
                              <v-icon color="grey lighten-1"
                                >mdi-trash-can
                              </v-icon>
                            </v-btn>
                          </v-row>
                        </v-list-item-action>
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card>
              </v-menu>
            </template>
          </v-slider>
        </v-flex>
      </v-layout>
    </v-card>
    <!-- </v-menu> -->
  </div>
</template>

<script>
import EditName from "./EditName.vue";

export default {
  components: {
    EditName,
  },
  data: () => ({
    historyBtn: 0,
    playBtn: 0,
    badge: 0,
    player: false,
    menu: false,
    sheet: true,
    isPlaying: false,
    isDisabled: true,
    position: 0,
    userName: "Robotic Musicianship",
    currentAudio: null,
    selectedItem: 0,
    lockSelection: false,
    items: [], //[{ audioId: "012345678",audioName:"Mashup 1", audioSrc:"AAAAAAAAAZZZZZZSSSSFBBBBBBB" }]
  }),
  watch: {
    historyBtn(value) {
      this.$emit("historyBtn", value);
    },
    playBtn(value) {
      this.$emit("playBtn", value);
    },
    currentAudio(value) {
      if (!value) {
        this.isDisabled = true;
      } else {
        this.isDisabled = false;
      }
    },
    items(value) {
      this.currentAudio = value[0];
    },
    selectedItem(value) {
      try {
        let selectedAudioId = this.items[value].audioId;
        this.$emit("audioSelected", selectedAudioId); //send a message to mixboard.vue
        this.currentAudio = this.items[value];
      } catch {
        console.error("error");
      }
    },
  },
  methods: {
    test() {
      console.log(this.history);
    },
    clearBadge() {
      //add the click track
      this.historyBtn += 1;
      //reset the badge to 0
      this.badge = 0;
    },
    addDownloadLink(item) {
      let download = document.getElementById(`download${item.downloadId}`);
      download.innerHTML = "download";
    },
    toggleSongPlay() {
      this.playBtn += 1;
      // this.isDisabled = false;
      if (this.isPlaying === false) {
        // emit play
        this.$emit("play");
      } else if (this.isPlaying === true) {
        // emit stop
        this.$emit("stop");
      }
    },
    previousSong() {
      let value = this.selectedItem - 1;
      try {
        let selectedAudioId = this.items[value].audioId;
        this.$emit("audioSelected", selectedAudioId);
        this.currentAudio = this.items[value];
      } catch {
        console.error("error");
      }
    },
    nextSong() {
      let value;
      if (this.selectedItem !== this.items.length - 1) {
        value = this.selectedItem + 1;
      } else if (this.selectedItem === this.items.length - 1) {
        value = 0;
      }
      try {
        let selectedAudioId = this.items[value].audioId;
        this.$emit("audioSelected", selectedAudioId);
        this.currentAudio = this.items[value];
      } catch {
        console.error("error");
      }
    },
    dragSlider(value) {
      let percent = value / 1000;
      this.$emit("positionChange", percent);
    },
    editName(item, name) {
      item.audioName = name;
    },
    sendAudioName(audioName, audioId) {
      let editNameArray = this.$refs.editName;
      // find the index of the right ref
      let idx = editNameArray.findIndex(
        (object) => object.$parent.$attrs.id == audioId
      );
      this.$refs.editName[idx].value = audioName;
    },
    removeAudio(audio) {
      //confirm from the user if they really want to delete
      //if yes, delete the audio from playlist and mixboard history
      //delete from playlist
      let playlist = this.items;

      function isItem(item) {
        return item.audioId === audio.audioId;
      }

      let itemIndex = playlist.findIndex(isItem);
      playlist.splice(itemIndex, 1);
      //delete from main history
      this.$emit("deleteAudio", audio);
    },
    addEventListeners() {
      document.addEventListener("keyup", (event) => {
        if (event.code === "Space") {
          event.preventDefault();
          // console.log("Space pressed");
        }
      });
    },
  },
  mounted() {
    // this.addEventListeners();
  },
};
</script>

<style scoped></style>
