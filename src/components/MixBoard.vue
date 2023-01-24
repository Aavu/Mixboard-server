<template>
  <v-layout class="pa-2">
    <v-row justify="space-around">
      <v-col cols="12" lg="2" md="2" sm="2" xl="2">
        <v-row>
          <ClipBoard
            style="width: 80%"
            ref="clipboard"
            @confirmDeleteSong="confirmDeleteSong"
            @confirmSongChange="confirmSongChange"
            @confirmAddSong="confirmAddSong"
            @dragend="dragend"
            @dragging="drag"
            @updateDownloaded="updateGenMsg"
            @randomSongs="
              clickTracking.randomSongs += 1;
              totalClick += 1;
            "
          />
        </v-row>
        <v-switch
          v-model="lane_link"
          :label="`lane_link: ${lane_link.toString()}`"
        ></v-switch>
        <v-switch
          v-model="section_sync"
          :label="`section_sync: ${section_sync.toString()}`"
        ></v-switch>
        <!-- <v-btn @click="test">test</v-btn> -->
        <v-row justify="center">
          <div id="generatedAudio"></div>
        </v-row>
      </v-col>
      <v-col
        id="mixboard-container"
        class="mixboard-container"
        cols="12"
        lg="10"
        md="10"
        sm="10"
        style="padding-right: 2rem; padding-bottom: 2rem; padding-left: 0rem"
      >
        <v-row>
          <v-col cols="12" lg="1" md="1" sm="1">
            <div></div>
          </v-col>
          <v-col cols="12" lg="11" md="11" sm="11">
            <bar-axis
              ref="barAxis"
              :barNumber="colNum"
              @getPercent="seekAudio"
            ></bar-axis>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" lg="1" md="1" sm="1">
            <div id="text-container">
              <div v-for="lane in lanes" :key="lane.text">
                <p class="laneName noselect">{{ lane.name }}</p>
              </div>
            </div>
          </v-col>
          <v-col cols="12" lg="11" md="11" sm="11">
            <div id="container">
              <div id="fourLanes">
                <div v-for="lane in lanes" :key="lane.name">
                  <div :id="lane.id" class="content">
                    <grid-layout
                      id="gridLayout"
                      :key="lane.layoutKey"
                      :ref="'gridlayout' + lane.id"
                      :auto-size="false"
                      :col-num="colNum"
                      :is-draggable="isDraggable"
                      :is-mirrored="false"
                      :is-resizable="isResizable"
                      :layout.sync="lane.layout"
                      :margin="[5, 10]"
                      :max-rows="-1"
                      :prevent-collision="true"
                      :row-height="17"
                      :use-css-transforms="true"
                      :vertical-compact="true"
                      class="grid-widget"
                    >
                      <div class="grid-layout-content">
                        <!-- <span class="text">
                      <h1 class="dynamic-text-shadow noselect">
                        {{ lane.name }}
                      </h1></span
                    > -->
                      </div>
                      <grid-item
                        v-for="item in lane.layout"
                        :key="item.i.toString()"
                        :class="item.class"
                        :h="item.h"
                        :i="item.i.toString()"
                        :maxH="item.h"
                        :minH="item.h"
                        :w="item.w"
                        :x="item.x"
                        :y="item.y"
                        @move="moveItem(item)"
                        @moved="moveEnd(item, lane.layout)"
                      >
                        <div
                          class="grid-item-content"
                          @mouseleave="item.del = false"
                          @mouseover="item.del = true"
                        >
                          <!-- <span
                        class="text noselect songname"
                        style="white-space: nowrap"
                        >{{ item.item.songName }}</span
                      > -->
                          <span
                            v-show="item.del"
                            class="remove"
                            @click="removeItem(item.i, lane.layout)"
                          >
                            <v-icon color="white">mdi-delete</v-icon>
                          </span>
                          <div v-for="n in 15" :key="`${item.item}img${n}`">
                            <v-img
                              :src="item.item.img_url"
                              alt="image"
                              blank-color="#4A63A1"
                              class="ml-2 mt-4 d-flex pa-1 albumCover"
                              :aspect-ratio="1 / 1"
                              :min-width="imgSize"
                              :max-width="imgSize"
                            ></v-img>
                          </div>
                        </div>
                      </grid-item>
                    </grid-layout>
                  </div>
                </div>
                <long-playline
                  ref="largeCanvas"
                  v-show="showOverlay"
                ></long-playline>
              </div>
            </div>
          </v-col>
        </v-row>

        <v-row align="center" justify="baseline" wrap style="margin-top: 0px">
          <v-col
            cols="12"
            sm="1"
            md="2"
            lg="2"
            xl="2"
            style="padding-left: 3rem"
          >
            <v-btn
              :disabled="isDisabled"
              class="white--text"
              color="#7f91bc"
              @click="generateAudio"
            >
              Generate
            </v-btn>
          </v-col>
          <v-col cols="12" sm="1" md="2" lg="2" xl="2">
            <v-btn
              class="pink white--text"
              @click="luckyMe"
              :disabled="isDisabledLucky"
            >
              luckyMe
              <v-icon title="random selection">mdi-dice-3-outline</v-icon>
            </v-btn>
          </v-col>
          <v-col cols="12" lg="6" md="6" sm="6" xl="6">
            <output-audio
              ref="outputAudio"
              @audioSelected="audioPrep"
              @deleteAudio="deleteHistory"
              @play="playAudio"
              @positionChange="seekAudio"
              @stop="pauseAudio"
              @historyBtn="
                clickTracking.historyBtn += 1;
                totalClick += 1;
              "
              @playBtn="
                clickTracking.playBtn += 1;
                totalClick += 1;
              "
            ></output-audio>
          </v-col>
          <v-col cols="12" lg="2" md="2" sm="2" xl="2">
            <v-btn
              class="white--text"
              color="#7f91bc"
              @click="
                dialog = true;
                clickTracking.clearCanvas += 1;
                totalClick += 1;
              "
              :disabled="isDisabled"
            >
              clear canvas
            </v-btn>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <v-dialog
      v-model="processing"
      hide-overlay
      persistent
      width="300px"
      height="500px"
    >
      <v-card color="#7f91bc" dark class="pt-5">
        <!-- <v-btn icon @click="processing = false">x</v-btn> -->
        <v-card-text>
          <v-row justify="center"
            ><span color="#f8f8ff" style="font-weight: bold !important">{{
              genMsg
            }}</span></v-row
          >
          <v-row class="pa-md-1">
            <v-progress-linear
              class="mb-0"
              v-model="value"
              buffer-value="0"
              color="white"
              stream
            ></v-progress-linear>
          </v-row>
          <v-row justify="center"
            ><span color="#f8f8ff" style="font-weight: bold !important"
              >{{ value }}%</span
            ></v-row
          >
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialog" max-width="290" persistent>
      <v-card>
        <v-card-title class="text-h5">
          Are you sure you want to clear the canvas?
        </v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="#4A63A1" text @click="dialog = false"> Cancel</v-btn>
          <!--<v-btn color="green darken-1" text @click="confirmClear">-->
          <v-btn color="#4A63A1" text @click="confirmClear"> Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <pop-up ref="popup"></pop-up>
  </v-layout>
</template>

<script>
import ClipBoard from "./ClipBoard";
import VueGridLayout from "vue-grid-layout";
import BarAxis from "./BarAxis.vue";
import OutputAudio from "./OutputAudio.vue";
import PopUp from "./PopUp.vue";
import LongPlayline from "./LongPlayline.vue";

let mouseXY = { x: null, y: null };
let mousePosition = { x: null, y: null };
// let DragPos = { x: null, y: null, w: 1, h: 1, i: null };
const axios = require("axios").default;
// axios.defaults.timeout = 1000 * 180;
let windowInterval = 0;
let host =
  window.location.protocol +
  "//" +
  window.location.hostname +
  ":" +
  window.location.port;
export default {
  data: () => ({
    lane_link: true,
    section_sync: false,
    baseUri: host,
    genMsg: "Mashing up",
    value: 0,
    showOverlay: true,
    processing: false,
    dialog: false,
    isDraggable: true,
    isResizable: true,
    isDisabled: true,
    isDisabledLucky: false,
    isDownloading: [], //create a list of song that is downloading
    colNum: 32,
    avgTempo: null,
    fullScreenSecond: null,
    containerWidth: 0,
    defaultClipWidth: 4,
    lastActiveLane: null,
    removeBtn: false,
    isDragging: { x: null, y: null },
    history: {}, //Each history object: key is the audioId, and the corresponding value is a version of lanes. 18409345:[{Vocal_lane},{Instruments_lane},{},{}]
    color_theme: null, //when mounted, a color theme will be chosen from color_palatte
    color_palatte: [
      {
        name: "theme1",
        slots: ["#8F36AA", "#020060", "#182CD9", "#6FA0EA"],
        highlight: "#D300D8",
      },
      {
        name: "theme2",
        slots: ["#4F0373", "#245E6A", "#1E2DB4", "#567EBB"],
        highlight: "#00FB37",
      },
      {
        name: "theme3",
        slots: ["#7000FF", "#001AFF", "#195042", "#00BFFA"],
        highlight: "#05FEC2",
      },
      {
        name: "theme4",
        slots: ["#5B277A", "#03008F", "#6A85E3", "#026378"],
        highlight: "#FAFF00",
      },
      {
        name: "theme5",
        slots: ["#700229", "#510077", "#2C00AA", "#3E0627"],
        highlight: "#FF4D00",
      },
    ],
    lanes: [
      {
        name: "Vocal",
        text: "vocalText",
        layoutKey: "vocalLayout",
        id: "v001",
        mouseover: false,
        layout: [],
      },
      {
        name: "Instruments",
        text: "InstrumentsText",
        layoutKey: "instrumentsLayout",
        id: "i002",
        mouseover: false,
        layout: [],
      },
      {
        name: "Bass",
        text: "bassText",
        layoutKey: "bassLayout",
        id: "b003",
        mouseover: false,
        layout: [
          // { x: 0, y: 0, w: 2, h: 4.5, i: "0", del: false },
          // { x: 2, y: 0, w: 2, h: 4.5, i: "1", del: false },
          // { x: 4, y: 0, w: 2, h: 4.5, i: "2", del: false },
          // { x: 6, y: 0, w: 2, h: 4.5, i: "3", del: false },
        ],
      },
      {
        name: "Drum",
        text: "drumText",
        layoutKey: "drumLayout",
        id: "d004",
        mouseover: false,
        layout: [],
      },
    ],
    audioIsPlaying: false,
    currentPlayingAudio: null,
    currentPlaybackTime: null,
    luckyMeTemplates: {
      4: [
        {
          randomGen: true,
          tracksUsed: -1,
          v001: { blockNum: 3, minWidthFactor: 2 },
          i002: { blockNum: 2, minWidthFactor: 0 },
          b003: { blockNum: 2, minWidthFactor: 0 },
          d004: { blockNum: 4, minWidthFactor: -1 },
        },
        {
          randomGen: false,
          tracksUsed: 4,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [16, 28],
            ],
            tracks: [4, 5],
          },
          i002: { blockNum: 1, blocks: [[24, 32]], tracks: [6] },
          b003: {
            blockNum: 2,
            blocks: [
              [4, 16],
              [18, 32],
            ],
            tracks: [6, 6],
          },
          d004: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [12, 32],
            ],
            tracks: [5, 4],
          },
        },
        {
          randomGen: false,
          tracksUsed: 4,
          v001: {
            blockNum: 2,
            blocks: [
              [8, 16],
              [20, 32],
            ],
            tracks: [1, 3],
          },
          i002: {
            blockNum: 2,
            blocks: [
              [16, 24],
              [25, 32],
            ],
            tracks: [0, 2],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [4, 12],
              [13, 20],
            ],
            tracks: [2, 3],
          },
          d004: {
            blockNum: 2,
            blocks: [
              [0, 16],
              [17, 32],
            ],
            tracks: [0, 1],
          },
        },
        {
          randomGen: false,
          tracksUsed: 4,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [24, 32],
            ],
            tracks: [0, 2],
          },
          i002: {
            blockNum: 2,
            blocks: [
              [4, 12],
              [20, 28],
            ],
            tracks: [1, 1],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [8, 16],
              [16, 24],
            ],
            tracks: [2, 0],
          },
          d004: {
            blockNum: 3,
            blocks: [
              [0, 6],
              [12, 18],
              [24, 30],
            ],
            tracks: [3, 3, 3],
          },
        },
        {
          randomGen: false,
          tracksUsed: 4,
          v001: {
            blockNum: 1,
            blocks: [[10, 21]],
            tracks: [0],
          },
          i002: {
            blockNum: 2,
            blocks: [
              [0, 16],
              [16, 32],
            ],
            tracks: [1, 0],
          },
          b003: {
            blockNum: 4,
            blocks: [
              [0, 8],
              [8, 16],
              [16, 24],
              [24, 32],
            ],
            tracks: [2, 3, 2, 3],
          },
          d004: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [28, 32],
            ],
            tracks: [1, 1],
          },
        },
        {
          randomGen: false,
          tracksUsed: 4,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 10],
              [20, 32],
            ],
            tracks: [0, 0],
          },
          i002: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [14, 26],
            ],
            tracks: [1, 2],
          },
          b003: {
            blockNum: 1,
            blocks: [[0, 24]],
            tracks: [3],
          },
          d004: {
            blockNum: 1,
            blocks: [[8, 32]],
            tracks: [1],
          },
        },
        {
          randomGen: false,
          tracksUsed: 3,
          v001: {
            blockNum: 4,
            blocks: [
              [0, 4],
              [8, 12],
              [16, 20],
              [24, 28],
            ],
            tracks: [0, 0, 0, 1],
          },
          i002: {
            blockNum: 1,
            blocks: [[3, 29]],
            tracks: [2],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [0, 12],
              [16, 25],
            ],
            tracks: [0, 0],
          },
          d004: {
            blockNum: 1,
            blocks: [[4, 28]],
            tracks: [1],
          },
        },
      ],
      3: [
        {
          randomGen: false,
          tracksUsed: 3,
          v001: {
            blockNum: 2,
            blocks: [
              [12, 24],
              [24, 32],
            ],
            tracks: [1, 0],
          },
          i002: { blockNum: 1, blocks: [[8, 20]], tracks: [2] },
          b003: {
            blockNum: 2,
            blocks: [
              [0, 12],
              [16, 26],
            ],
            tracks: [0, 0],
          },
          d004: {
            blockNum: 2,
            blocks: [
              [4, 16],
              [17, 32],
            ],
            tracks: [1, 2],
          },
        },
        {
          randomGen: false,
          tracksUsed: 3,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 16],
              [20, 32],
            ],
            tracks: [0, 2],
          },
          i002: { blockNum: 1, blocks: [[16, 28]], tracks: [1] },
          b003: { blockNum: 1, blocks: [[8, 20]], tracks: [2] },
          d004: {
            blockNum: 2,
            blocks: [
              [0, 16],
              [17, 28],
            ],
            tracks: [1, 0],
          },
        },
        {
          randomGen: false,
          tracksUsed: 3,
          v001: {
            blockNum: 4,
            blocks: [
              [0, 4],
              [8, 12],
              [16, 20],
              [24, 28],
            ],
            tracks: [0, 0, 0, 1],
          },
          i002: {
            blockNum: 1,
            blocks: [[3, 29]],
            tracks: [2],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [0, 12],
              [16, 25],
            ],
            tracks: [0, 0],
          },
          d004: {
            blockNum: 1,
            blocks: [[4, 28]],
            tracks: [1],
          },
        },
        {
          randomGen: false,
          tracksUsed: 3,
          v001: {
            blockNum: 4,
            blocks: [
              [0, 4],
              [8, 12],
              [16, 20],
              [24, 28],
            ],
            tracks: [0, 0, 0, 1],
          },
          i002: {
            blockNum: 2,
            blocks: [
              [4, 16],
              [20, 32],
            ],
            tracks: [1, 2],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [20, 28],
            ],
            tracks: [2, 0],
          },
          d004: {
            blockNum: 1,
            blocks: [[0, 20]],
            tracks: [1],
          },
        },
      ],
      2: [
        {
          randomGen: false,
          tracksUsed: 2,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [16, 28],
            ],
            tracks: [1, 1],
          },
          i002: { blockNum: 1, blocks: [[12, 20]], tracks: [0] },
          b003: {
            blockNum: 2,
            blocks: [
              [4, 16],
              [20, 32],
            ],
            tracks: [1, 0],
          },
          d004: {
            blockNum: 3,
            blocks: [
              [0, 12],
              [12, 24],
              [24, 32],
            ],
            tracks: [0, 1, 0],
          },
        },
        {
          randomGen: false,
          tracksUsed: 2,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 16],
              [24, 32],
            ],
            tracks: [0, 0],
          },
          i002: { blockNum: 1, blocks: [[16, 28]], tracks: [1] },
          b003: { blockNum: 1, blocks: [[2, 16]], tracks: [1] },
          d004: {
            blockNum: 2,
            blocks: [
              [8, 24],
              [24, 32],
            ],
            tracks: [0, 1],
          },
        },
        {
          randomGen: false,
          tracksUsed: 2,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [16, 28],
            ],
            tracks: [0, 0],
          },
          i002: {
            blockNum: 1,
            blocks: [[0, 21]],
            tracks: [1],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [6, 15],
              [17, 29],
            ],
            tracks: [0, 1],
          },
          d004: {
            blockNum: 2,
            blocks: [
              [3, 15],
              [24, 32],
            ],
            tracks: [0, 1],
          },
        },
        {
          randomGen: false,
          tracksUsed: 2,
          v001: {
            blockNum: 1,
            blocks: [[0, 16]],
            tracks: [0],
          },
          i002: {
            blockNum: 1,
            blocks: [[16, 24]],
            tracks: [1],
          },
          b003: {
            blockNum: 1,
            blocks: [[0, 8]],
            tracks: [1],
          },
          d004: {
            blockNum: 2,
            blocks: [
              [8, 24],
              [24, 32],
            ],
            tracks: [0, 1],
          },
        },
      ],
      1: [
        {
          randomGen: false,
          tracksUsed: 1,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [16, 24],
            ],
            tracks: [0, 0],
          },
          i002: {
            blockNum: 2,
            blocks: [
              [4, 16],
              [20, 28],
            ],
            tracks: [0, 0],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [12, 20],
              [24, 32],
            ],
            tracks: [0, 0],
          },
          d004: { blockNum: 1, blocks: [[8, 32]], tracks: [0] },
        },
        {
          randomGen: false,
          tracksUsed: 1,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 4],
              [16, 32],
            ],
            tracks: [0, 0],
          },
          i002: {
            blockNum: 1,
            blocks: [[0, 25]],
            tracks: [0],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [8, 12],
              [21, 32],
            ],
            tracks: [0, 0],
          },
          d004: {
            blockNum: 1,
            blocks: [[0, 16]],
            tracks: [0],
          },
        },
        {
          randomGen: false,
          tracksUsed: 1,
          v001: {
            blockNum: 2,
            blocks: [
              [0, 4],
              [16, 32],
            ],
            tracks: [0, 0],
          },
          i002: {
            blockNum: 1,
            blocks: [[4, 8]],
            tracks: [0],
          },
          b003: {
            blockNum: 2,
            blocks: [
              [8, 12],
              [16, 32],
            ],
            tracks: [0, 0],
          },
          d004: {
            blockNum: 2,
            blocks: [
              [0, 8],
              [12, 16],
            ],
            tracks: [0, 0],
          },
        },
      ],
    },
    totalClick: 0,
    clickTracking: {
      luckyMe: 0,
      generateBtn: 0,
      randomSongs: 0,
      randomSong: 0,
      clearCanvas: 0,
      playBtn: 0,
      historyBtn: 0,
    },
  }),
  watch: {
    totalClick(value) {
      console.log("CurrentTotalClicks:", value);
      console.log(this.clickTracking);
    },
    processing(value) {
      if (value) {
        this.preventMoving();
      } else {
        this.allowMoving();
      }
    },
    audioIsPlaying(value) {
      let that = this;
      if (value === true) {
        this.$refs.outputAudio.isPlaying = true;
        this.showOverlay = true;
        // when the audio is playing, prevent the user from changing the layout, or click luckyme, or hit generate again
        this.preventMoving();
        windowInterval = window.setInterval(() => {
          let audio = document.getElementById(that.currentPlayingAudio.id);
          that.currentPlaybackTime = audio.currentTime;
          // console.log(that.currentPlaybackTime);
          //when audio starts to play, check each block and change their class, rest or active. show state by changing <style>
          that.changeBlockState(that.currentPlaybackTime);
        }, 100);
      } else {
        this.$refs.outputAudio.isPlaying = false;
        this.allowMoving();

        this.showOverlay = false;
        window.clearInterval(windowInterval);
        this.resetBlockState();
      }
    },

    currentPlaybackTime(playbackTime) {
      let avg_tempo = this.avg_tempo;
      let bar_num = this.colNum;
      let dur_bar_axis = (60 / avg_tempo) * 4 * bar_num; //the audio length of 32 bars
      //when audio playback time changes, refresh BarAxis and player progress
      this.$refs.barAxis.refreshBarAxis(playbackTime, dur_bar_axis);
      this.$refs.outputAudio.position = (playbackTime / dur_bar_axis) * 1000;
      this.$refs.largeCanvas.refreshCanvas(playbackTime, dur_bar_axis);
    },
    // isMovingItem(value) {
    //   if (value === true) {
    //     // console.log("isMovingItem: ", value);
    //     //addeventlistener, find activeLane
    //     // let activeLane = this.findActiveLane();
    //     // console.log(activeLane);
    //   }
    // },
  },
  components: {
    ClipBoard,
    GridLayout: VueGridLayout.GridLayout,
    GridItem: VueGridLayout.GridItem,
    BarAxis,
    OutputAudio,
    PopUp,
    LongPlayline,
  },
  computed: {
    imgSize() {
      return (this.containerWidth / 32) * 2.5 - 4;
    },
  },
  methods: {
    checkDownloading() {
      console.log("check if downloading song is in the layout");
      //check each slot in clipboard.vue, see if there is song downloading

      let slots = this.$refs.clipboard.slots;
      for (let i = 0; i < slots.length; i++) {
        let refName = slots[i].ref;
        let ref_slot = this.$refs.clipboard.$refs[refName][0];
        if (ref_slot.downloadProgress != -1) {
          //if the slot has song downloading, check the layout in mixboard.vue to see if there is downloading song in the layout
          // let songId = Object.keys(ref_slot.items)[0];
          // if (this.checkLayout(songId)) {
          //   return true;
          // }
          return true;
        }
      }
      return false;
    },
    checkLayout(songId) {
      //check if a song is contained in current layout, if yes, return ture, otherwise return false
      for (let i = 0; i < this.lanes.length; i++) {
        for (let j = 0; j < this.lanes[i].layout.length; j++) {
          let block = this.lanes[i].layout[j];
          let block_songId = block.item.songId;
          if (block_songId == songId) {
            console.log("block contains this songId!");
            console.log(block);
            console.log(songId);
            return true;
          }
        }
      }
      return false;
    },
    addBlockTimeInfo(tempo) {
      //after the song being generated, the song tempo info should be prepared already
      //tempo is the current playing song's tempo
      let time_per_bar = (60 / tempo) * 4; //seconds per bar, if tempo=60, then time_per_bar = 4 seconds
      for (let i = 0; i < this.lanes.length; i++) {
        for (let j = 0; j < this.lanes[i].layout.length; j++) {
          let block = this.lanes[i].layout[j];
          let block_start_time = block.x * time_per_bar;
          let block_end_time = (block.x + block.w) * time_per_bar;
          block.start_time = block_start_time;
          block.end_time = block_end_time;
        }
      }
    },
    changeBlockState(currentTime) {
      //currentTime is the time fetched when the song is playing in seconds
      for (let i = 0; i < this.lanes.length; i++) {
        for (let j = 0; j < this.lanes[i].layout.length; j++) {
          let block = this.lanes[i].layout[j];
          let block_start_time = block.start_time;
          let block_end_time = block.end_time;
          if (
            currentTime >= block_start_time &&
            currentTime <= block_end_time
          ) {
            // if current time is in between the block's start time and end time, that means block should be highlighted
            if (block.class.includes("activeBlock")) {
              continue;
            } else {
              console.log(block);
              block.class.push("activeBlock");
            }
          } else {
            if (block.class.indexOf("activeBlock") != -1) {
              block.class.splice(block.class.indexOf("activeBlock"), 1); //if the block should not be played at this moment, remove the activeBlock
            } else {
              continue;
            }
          }
        }
      }
    },
    resetBlockState() {
      for (let i = 0; i < this.lanes.length; i++) {
        for (let j = 0; j < this.lanes[i].layout.length; j++) {
          let block = this.lanes[i].layout[j];
          if (block.class.indexOf("activeBlock") != -1) {
            block.class.splice(block.class.indexOf("activeBlock"), 1);
          }
        }
      }
    },
    popup() {
      this.$refs.popup.overlay = true;
    },
    checkEmpty() {
      let lanes = this.lanes;
      for (let i = 0; i < lanes.length; i++) {
        if (lanes[i].layout.length !== 0) {
          return 1;
        }
      }
      return 0;
    }, //check if the layout is empty
    checkClipboard() {
      //check if clipboard is empty
      let clipboardContent = this.$refs.clipboard.slots;
      let clipboardRefs = [];
      for (let i = 0; i < clipboardContent.length; i++) {
        if (
          !(
            clipboardContent[i].item == null ||
            Object.keys(clipboardContent[i].item).length === 0
          )
        ) {
          clipboardRefs.push(i);
        }
      }
      return clipboardRefs; //no song in the clipboard
    },
    luckyMe() {
      //add a click count
      this.clickTracking.luckyMe += 1;
      this.totalClick = this.totalClick + 1;
      function getRandomInt(min, max) {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1) + min); //The maximum is inclusive and the minimum is inclusive
      }

      function getBlockWidth(id, maxWidth) {
        let random_width = {
          v001: getRandomInt(4, maxWidth),
          i002: getRandomInt(4, 12),
          b003: getRandomInt(4, 12),
          d004: getRandomInt(8, maxWidth),
        };

        return random_width[id];
      }

      function findOverlap(x, y, track, lane) {
        if (lane.layout.length === 0 || x === y) {
          return false;
        }

        for (let block of lane.layout) {
          let i = block.x;
          let j = i + block.w;

          if (y <= i || j <= x) {
            /* no block overlap */
            return false;
          } else {
            /* block overlap */
            if (block.item === track) {
              /* blocks have same track */
              return true;
            }
          }
        }
        return false;
      }

      function determineTrack(trackID) {
        switch (trackID) {
          case 4:
            return getRandomInt(0, 1);
          case 5:
            return getRandomInt(2, 3);
          case 6:
            return getRandomInt(0, 3);
          default:
            return trackID;
        }
      }

      function shuffle(array) {
        let currentIndex = array.length,
          randomIndex;

        // While there remain elements to shuffle.
        while (currentIndex !== 0) {
          // Pick a remaining element.
          randomIndex = Math.floor(Math.random() * currentIndex);
          currentIndex--;

          // And swap it with the current element.
          [array[currentIndex], array[randomIndex]] = [
            array[randomIndex],
            array[currentIndex],
          ];
        }

        return array;
      }

      let clipboardContent = this.$refs.clipboard.slots;
      let clipboardRefs = this.checkClipboard();
      let trackCount = clipboardRefs.length;

      if (trackCount !== 0) {
        this.clearCanvas();
        let songList = [];
        for (let i = 0; i < trackCount; i++) {
          songList.push(
            Object.values(clipboardContent[clipboardRefs[i]].item)[0]
          );
        }

        if (trackCount > 1) {
          songList = shuffle(songList);
        }

        let luck;
        let templateNum = this.luckyMeTemplates[trackCount].length - 1;
        if (templateNum === 0) {
          luck = this.luckyMeTemplates[trackCount][0];
        } else {
          luck =
            this.luckyMeTemplates[trackCount][getRandomInt(0, templateNum)];
        }

        for (let lane of this.lanes) {
          let laneVars = luck[lane.id];
          let blockNum = laneVars["blockNum"];
          let maxWidth = Math.floor(this.colNum / blockNum);
          let startPos = 0;
          let prevSong = null;
          let width = null;
          let song = null;

          for (let j = 0; j < blockNum; j++) {
            if (luck["randomGen"] === false) {
              /* Set block position on segment */
              let block = laneVars["blocks"][j];
              startPos = block[0];
              width = block[1] - startPos;

              /* Get track to play for the block */
              let trackID = determineTrack(laneVars["tracks"][j]);
              song = songList[trackID];
            } else {
              /* Calculate width for random block on segment */
              width = getBlockWidth(lane.id, maxWidth);

              /* Find track, no two consecutive same tracks*/
              song = songList[getRandomInt(0, trackCount - 1)];

              let idx = this.lanes.indexOf(lane) - 1;
              if (idx !== -1) {
                while (
                  findOverlap(
                    startPos,
                    startPos + width,
                    song,
                    this.lanes[idx]
                  ) === true
                ) {
                  song = songList[getRandomInt(0, trackCount - 1)];
                }
              }

              while (song === prevSong) {
                song = songList[getRandomInt(0, trackCount - 1)];
              }
            }

            let block = {
              x: startPos,
              y: 0,
              w: width,
              h: 4.5,
              i: j.toString(),
              del: false,
              class: [],
              item: song,
              id: this.generateUuid(),
            };
            //push song.class to block class
            // console.log("songclass is:", song.class);
            block.class.push(song.class);
            lane.layout.push(block);

            if (luck.randomGen === true) {
              if (lane.id !== "d004") {
                let endPos = startPos + width;
                maxWidth = Math.floor((this.colNum - endPos) / (blockNum - j));
                startPos =
                  startPos +
                  width +
                  getRandomInt(laneVars.minWidthFactor, maxWidth);
              } else {
                startPos = startPos + width;
              }
            }

            prevSong = song;
          }
        }
      } else {
        // console.log("add some songs first to get lucky!");
        alert("Add some songs first to get lucky!");
      }

      this.isDisabled = false;
    },
    preventMoving() {
      this.isDraggable = false;
      this.isResisable = false;
      this.$refs.outputAudio.lockSelection = true;
      //disable luckyme
      this.isDisabledLucky = true;
      //disable generate
      this.isDisabled = true;
      // prevent user from deleting the song card
      this.$refs.clipboard.deletableSlot = false;
      //prevent select four random songs
      this.$refs.clipboard.randomDisabled = true;
      //disable add song button in selectedSongs.vue
      let slots = this.$refs.clipboard.slots;
      for (let i = 0; i < slots.length; i++) {
        let refName = slots[i].ref;
        let ref_slot = this.$refs.clipboard.$refs[refName][0];
        ref_slot.preventAdd = true;
      }
    },
    allowMoving() {
      this.isDraggable = true;
      this.isResisable = true;
      this.$refs.outputAudio.lockSelection = false;
      //allow luckyme
      this.isDisabledLucky = false;
      //allow generate
      this.isDisabled = false;
      this.$refs.clipboard.deletableSlot = true;
      this.$refs.clipboard.randomDisabled = false;
      let slots = this.$refs.clipboard.slots;
      for (let i = 0; i < slots.length; i++) {
        let refName = slots[i].ref;
        let ref_slot = this.$refs.clipboard.$refs[refName][0];
        ref_slot.preventAdd = false;
      }
    },
    removeItem: function (val, layout) {
      if (this.audioIsPlaying || this.processing) {
        return;
      }
      const index = layout.map((item) => item.i).indexOf(val);
      layout.splice(index, 1);
    },
    moveItem: function (layoutItem) {
      //Once user move the block, remove the currentAudio in outputAudio.vue
      this.$refs.outputAudio.currentAudio = null;
      //layout Item contains the card Item Info
      console.log("dragging layout Item");
      console.log(layoutItem);
      this.dragEvent = 2; //change Drag event to show layout item is moved
      let activeLane = this.findActiveLane(mousePosition.x, mousePosition.y);
      console.log(mousePosition.x, mousePosition.y, activeLane);
    },
    moveEnd(item, layout) {
      console.log("moveEnd");
      let activeLane = this.findActiveLane(mousePosition.x, mousePosition.y);
      console.log("moveEnd,activeLaneIs", activeLane);
      if (activeLane == null) {
        console.log("drop out of the canvas or not changing the lane!");
        return;
      }
      if (item.lane !== activeLane) {
        console.log("drop in another lane");
        if (
          this.checkConfliction(activeLane, mousePosition.x, mousePosition.y)
        ) {
          return;
        }
        //delete item in the original lane, change item lane name, add into new lane
        this.removeItem(item.i, layout);
        item.lane = activeLane;
        let dropLane = this.findLaneById(activeLane);
        let length = dropLane.layout.length;
        //check how many items are there in dropLane now, calculate new item.i; if the drop lane is empty, item.i=0;
        if (length == 0) {
          item.i = "0";
        } else {
          item.i = String(parseInt(dropLane.layout[length - 1].i) + 1);
        }

        dropLane.layout.push(item);
      }
    },
    checkConfliction(activeLaneId, posX, posY) {
      // active lane actions
      let parentRect = document
        .getElementById(activeLaneId)
        .getBoundingClientRect();
      let activeLayoutIndex = this.lanes.findIndex((lane) => {
        return lane.id === activeLaneId;
      });
      let activeLayout = this.lanes[activeLayoutIndex].layout;
      // console.log("activeLaneId:", activeLaneId);

      if (
        posX > parentRect.left &&
        posX < parentRect.right &&
        posY > parentRect.top &&
        posY < parentRect.bottom
      ) {
        //////////////////////////////////

        let drag_item_x = Math.floor(
          (posX - parentRect.left) /
            ((parentRect.right - parentRect.left) / this.colNum)
        );
        if (
          activeLayout.findIndex((item) => {
            return (
              (drag_item_x + this.defaultClipWidth > item.x &&
                drag_item_x + this.defaultClipWidth <= item.x + item.w) ||
              (drag_item_x >= item.x &&
                drag_item_x + this.defaultClipWidth <= item.x + item.w) ||
              (drag_item_x >= item.x && drag_item_x < item.x + item.w)
            );
          }) !== -1
        ) {
          console.log("Item confliction");
          return true;
        }
      }
    },
    findLaneById(laneId) {
      let activeLaneIndex = this.lanes.findIndex((lane) => {
        return lane.id === laneId;
      });
      let found_lane = this.lanes[activeLaneIndex];
      return found_lane;
    },
    locateLane(lane, posX, posY) {
      let laneId = lane.id;
      let parentRect = document.getElementById(laneId).getBoundingClientRect();
      // let mouseInGrid = false;
      if (
        posX > parentRect.left &&
        posX < parentRect.right &&
        posY > parentRect.top &&
        posY < parentRect.bottom
      ) {
        // mouseInGrid = true;
        this.lastActiveLane = laneId;
        // console.log("mouseInGrid", laneId);
        return laneId;
      } else {
        return "noId";
      }
    },
    dragTo(activeLaneId, item, posX, posY) {
      if (activeLaneId == null) {
        return;
      }
      //delete temp blocks in other lanes
      for (let i = 0; i < this.lanes.length; i++) {
        if (this.lanes[i].id !== activeLaneId) {
          let tempIndex = this.lanes[i].layout.findIndex((layout_item) => {
            return layout_item.i === "temp";
          });
          console.log("tempIndex", tempIndex);
          if (tempIndex !== -1) {
            this.lanes[i].layout.splice(tempIndex, 1);
          }
        }
      }
      // active lane actions
      let parentRect = document
        .getElementById(activeLaneId)
        .getBoundingClientRect();
      let activeLayoutIndex = this.lanes.findIndex((lane) => {
        return lane.id === activeLaneId;
      });
      let activeLayout = this.lanes[activeLayoutIndex].layout;
      // console.log("activeLaneId:", activeLaneId);

      if (
        posX > parentRect.left &&
        posX < parentRect.right &&
        posY > parentRect.top &&
        posY < parentRect.bottom
      ) {
        ///////////////////////////////////
        let tempIndex = activeLayout.findIndex((item) => {
          return item.i === "temp";
        });
        if (tempIndex !== -1) {
          // console.log("Duplicate item");
          // update new position
          activeLayout[tempIndex].x = Math.floor(
            (posX - parentRect.left) /
              ((parentRect.right - parentRect.left) / this.colNum)
          );
          return;
        }
        //////////////////////////////////

        let drag_item_x = Math.floor(
          (posX - parentRect.left) /
            ((parentRect.right - parentRect.left) / this.colNum)
        );
        if (
          activeLayout.findIndex((item) => {
            return (
              (drag_item_x + this.defaultClipWidth > item.x &&
                drag_item_x + this.defaultClipWidth <= item.x + item.w) ||
              (drag_item_x >= item.x &&
                drag_item_x + this.defaultClipWidth <= item.x + item.w) ||
              (drag_item_x >= item.x && drag_item_x < item.x + item.w)
            );
          }) !== -1
        ) {
          // console.log("Item confliction");
          return;
        }
        let block = {
          x: drag_item_x,
          y: 0,
          w: this.defaultClipWidth,
          h: 4.5,
          i: "temp",
          del: false,
          class: [],
          item: item,
          lane: activeLaneId,
        };
        activeLayout.push(block);
        block.class.push(item.class);
        console.log("item class is:", item.class);
      }
    },
    findActiveLane(posX, posY) {
      let lanes = this.lanes;
      let activeLane;
      for (let i = 0; i < lanes.length; i++) {
        activeLane = this.locateLane(lanes[i], posX, posY);
        if (activeLane !== "noId") {
          // break;
          return activeLane;
        }
      }
      if (activeLane === "noId") {
        // console.log("ActiveLane:", activeLane);
        return null;
      }
    },
    drag: function (item) {
      //if song is mashing up or is playing, prevent drag
      if (this.processing || this.audioIsPlaying) {
        return;
      }
      //if song is downloading, prevent drag
      let slot_num = item.class.charAt(item.class.length - 1);
      let slot_ref_name = "selectedSongs" + slot_num;
      // console.log("slot_ref_name:", slot_ref_name);
      let slot_ref = this.$refs.clipboard.$refs[slot_ref_name][0];
      if (slot_ref.spotifyOverlay) {
        // console.log("the song is downloading, please wait");
        return;
      }
      // console.log(item);
      let activeLane = this.findActiveLane(mouseXY.x, mouseXY.y);
      this.dragTo(activeLane, item, mouseXY.x, mouseXY.y);
    },

    dragend: function () {
      let lanes = this.lanes;
      let activeLane;
      for (let i = 0; i < lanes.length; i++) {
        activeLane = this.locateLane(lanes[i], mouseXY.x, mouseXY.y);
        // Find the drop lane
        if (activeLane !== "noId") {
          // let activeLaneIndex = this.lanes.findIndex((lane) => {
          //   return lane.id === activeLane;
          // });
          // let dropLane = this.lanes[activeLaneIndex];
          let dropLane = this.findLaneById(activeLane);
          let tempIndex = dropLane.layout.findIndex((layout_item) => {
            return layout_item.i === "temp";
          });
          // console.log("tempIndex:", tempIndex);
          if (tempIndex !== -1 && tempIndex !== 0) {
            // console.log(dropLane.layout[tempIndex]);
            dropLane.layout[tempIndex].i = String(
              parseInt(dropLane.layout[tempIndex - 1].i) + 1
            );
            // dropLane.layout[tempIndex].i = "newTemp";
          } else if (tempIndex === 0) {
            // console.log("The first block!");
            dropLane.layout[tempIndex].i = "0";
          }
          break;
        }
      }
      if (activeLane === "noId") {
        // console.log("drop out of lanes");
        let activeLaneIndex = this.lanes.findIndex((lane) => {
          return lane.id === this.lastActiveLane;
        });
        // console.log("last active lane:", activeLaneIndex);
        // let tempItemIndex = this.lanes[activeLaneIndex].layout.findIndex(
        //   (item) => {
        //     item.i === "temp";
        //   }
        // );
        let lastLayout = this.lanes[activeLaneIndex].layout;
        if (lastLayout[lastLayout.length - 1].i === "temp") {
          // console.log("delete temp");
          this.lanes[activeLaneIndex].layout.splice(-1, 1);
        }
      } else if (!this.processing && !this.audioIsPlaying) {
        this.isDisabled = false;
      }
    },
    mouseoverListener() {
      let vocalLane = document.getElementById("v001");
      let instrumentsLane = document.getElementById("i002");
      let bassLane = document.getElementById("b003");
      let drumLane = document.getElementById("d004");
      let lanes = [
        { name: "Vocal", div: vocalLane },
        { name: "Instruments", div: instrumentsLane },
        { name: "Bass", div: bassLane },
        { name: "Drum", div: drumLane },
      ];
      for (let i = 0; i < lanes.length; i++) {
        let laneName = lanes[i].name;
        let laneDiv = lanes[i].div;
        let that = this;
        laneDiv.addEventListener(
          "mouseenter",
          function () {
            let index = that.lanes.findIndex((lane) => {
              return lane.name === laneName;
            });
            // console.log(index);
            that.lanes[index].mouseover = true;
            // console.log(that.lanes[0].mouseover);
            // console.log(that.lanes[1].mouseover);
            // console.log(that.lanes[2].mouseover);
            // console.log(that.lanes[3].mouseover);
          },
          false
        );
        laneDiv.addEventListener(
          "mouseout",
          function () {
            let index = that.lanes.findIndex((lane) => {
              return lane.name === laneName;
            });
            that.lanes[index].mouseover = false;
          },
          false
        );
      }
    },

    confirmAddSong(song) {
      let songId = Object.keys(song)[0];
      for (let i = this.lanes.length - 1; i >= 0; i--) {
        let layout = this.lanes[i].layout;
        for (let j = layout.length - 1; j >= 0; j--) {
          let itemId = layout[j].item.songId;
          if (itemId === songId) {
            layout.splice(j, 1);
          }
        }
      }

      // console.log("confirm add song in mb", song);
      // var arr = this.baseUri + "/addSong";

      // let userData = { url: String(songId) };
      // let taskID = axios.post(arr, userData).then(async (response) => {
      //   console.log("add response:", response);
      //   return String(response.data.task_id);
      // });
      // // trigger spotify search updatestatus(taskID)
    },

    getTempoFromServer() {
      let arr = this.baseUri + "/getTempo";
      axios.get(arr, null).then(async (response) => {
        console.log("get tempo:", response.data);
        return String(response.data);
      });
    },

    confirmSongChange(song) {
      let songId = Object.keys(song)[0];
      for (let i = this.lanes.length - 1; i >= 0; i--) {
        let layout = this.lanes[i].layout;
        for (let j = layout.length - 1; j >= 0; j--) {
          let itemId = layout[j].item.songId;
          if (itemId === songId) {
            layout.splice(j, 1);
          }
        }
      }

      console.log("confirm add song in mb", song);
      let arr = this.baseUri + "/addSong";

      let userData = { url: String(songId) };
      axios.post(arr, userData).then(async (response) => {
        return String(response.data.task_id);
      });
    },

    confirmDeleteSong(song) {
      console.log("confirmDeleteSong", song);
      let songId = song.songId;
      for (let i = this.lanes.length - 1; i >= 0; i--) {
        let layout = this.lanes[i].layout;
        for (let j = layout.length - 1; j >= 0; j--) {
          let itemId = layout[j].item.songId;
          if (itemId === songId) {
            layout.splice(j, 1);
          }
        }
      }

      console.log("confirm delete song in mb", songId);
      let arr = this.baseUri + "/removeSong";

      let userData = { url: String(songId) };
      axios.post(arr, userData).then(async (response) => {
        return String(response.data.task_id);
      });
    },
    updateGenMsg() {
      this.genMsg = "Mashing up";
    },

    // Refer: https://stackoverflow.com/questions/12223529/create-globally-unique-id-in-javascript?noredirect=1&lq=1
    generateUuid(separator) {
      let delim = separator || "-";
      function S4() {
        return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
      }
      let st =
        new Date().getTime().toString(16).slice(0, 11) +
        (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1, 2);
      return (
        S4() + S4() + delim + S4() + delim + S4() + delim + S4() + delim + st
      );
    },

    async generateAudio() {
      //add a click count
      this.clickTracking.generateBtn += 1;
      this.totalClick += 1;
      //after user click the generate button
      //check if the layout is empty
      if (this.checkEmpty() === 0) {
        return;
      }
      //when there is downloading songs in the layout, remind the user to wait
      if (this.checkDownloading()) {
        console.log("there are downloading songs in the layout");
        this.genMsg = "Downloading songs...";
      }
      //disable moving blocks

      this.processing = true; //process bar show up
      this.value = 0;
      this.preventMoving();

      let arr = this.baseUri + "/generate";

      let userData = {};
      // userData.email = "testUser@gmail.com";
      userData.sessionId = this.generateUuid();
      userData.data = {};
      Object.assign(userData.data, this.lanes);
      //add two switch button info
      userData.data.lane_link = this.lane_link;
      userData.data.section_sync = this.section_sync;
      console.log("userData:", userData);

      let taskID = await axios.post(arr, userData).then(async (response) => {
        return String(response.data.task_id);
      });

      let pollingResponse = await this.getTaskStatus(taskID, this.baseUri);
      // console.log("Operation status is " + pollingResponse.task_status);
      console.log(pollingResponse);
      while (pollingResponse.requestStatus !== "SUCCESS") {
        if (pollingResponse.requestStatus === "FAILURE") {
          alert("Generation failed, try again!");
          return;
        }

        pollingResponse = await this.getTaskStatus(taskID, this.baseUri);
        // console.log(pollingResponse);
        if (pollingResponse.requestStatus === "PROGRESS") {
          // console.log(pollingResponse);
          this.value = pollingResponse.task_result.progress;
          // console.log("Generation " + this.value + "% done.");
        }
      }

      console.log("Fetching result...");
      let { snd: b64buf, tempo } = await this.fetchResult(taskID, this.baseUri);
      console.log("Result fetched!");
      this.avg_tempo = tempo;
      console.log("tempo ", tempo);
      this.addBlockTimeInfo(this.avg_tempo);

      let newAudio = document.createElement("audio");
      newAudio.id = Date.now();

      // newAudio.controls = "controls";
      newAudio.type = "audio/aac";
      newAudio.src = "data:audio/aac;base64, " + b64buf;
      document.getElementById("generatedAudio").appendChild(newAudio);
      this.processing = false; //process bar vanish
      this.$refs.outputAudio.position = 0; //player's position set to 0

      //save the layout version
      this.history[newAudio.id] = new Object();
      this.history[newAudio.id].layout = JSON.parse(JSON.stringify(this.lanes));
      //save the selected songs
      this.history[newAudio.id].clipboard = JSON.parse(
        JSON.stringify(this.$refs.clipboard.slots)
      );
      console.log("save history", this.$refs.clipboard.slots);
      console.log(
        "result of saving history:",
        this.history[newAudio.id].clipboard
      );
      // update the central player list
      let newOutputItem = {};
      newOutputItem.audioId = newAudio.id;
      newOutputItem.audioName = `Mashup ${Object.keys(this.history).length}`;
      newOutputItem.audioSrc = newAudio.src;
      newOutputItem.downloadId = `download${newAudio.id}`;
      newOutputItem.timeStamp = this.getTimeStamp();
      this.$refs.outputAudio.items.unshift(newOutputItem);
      this.$refs.outputAudio.badge++;

      this.currentPlayingAudio = document.getElementById(newAudio.id);
      this.sendInfoToBarAxis();
      let that = this;

      newAudio.addEventListener("play", (value) => {
        that.currentPlayingAudio = null; //reset other playing Audio
        // console.log(`Audio${value.target.id} is playing`);
        that.audioIsPlaying = true;
        that.currentPlayingAudio = value.target;
      });

      newAudio.addEventListener("pause", () => {
        that.audioIsPlaying = false;
      });

      newAudio.addEventListener("stop", () => {
        that.audioIsPlaying = false;
      });

      this.isDisabled = false;
      this.$refs.outputAudio.isDisabled = false;
      this.allowMoving();
    },
    sendInfoToBarAxis() {
      //user click generate, MixBoard.vue send avg_tempo and the (audioLength/32bar_audioLength) to BarAxis.vue
      this.fullScreenSecond = (60 / this.avg_tempo) * 4 * this.colNum;
      this.$refs.barAxis.fullScreenSecond = this.fullScreenSecond;
      this.$refs.barAxis.currentAudio = this.currentPlayingAudio;
    },

    clearCanvas() {
      let lanes = this.lanes;
      for (let i = 0; i < lanes.length; i++) {
        let lane = lanes[i];
        lane.layout = [];
      }
    },
    confirmClear() {
      this.clearCanvas();
      this.dialog = false;
      this.isDisabled = true;
    },

    seekAudio(percent) {
      try {
        // console.log(percent);
        let duration = this.currentPlayingAudio.duration;
        let full_duration = this.fullScreenSecond;
        let seekToTime = duration * percent;
        let audio = document.getElementById(this.currentPlayingAudio.id);
        audio.pause();
        audio.currentTime = seekToTime;
        // this.$refs.barAxis.drawPlayLine(seekToTime, duration);
        this.$refs.barAxis.refreshBarAxis(seekToTime, full_duration);
      } catch (error) {
        console.log("error");
      }
    },
    audioPrep(audioId) {
      this.currentPlayingAudio = document.getElementById(audioId);
      this.slotPrep(audioId);

      console.log("pulling layout...");
      let layoutVersion = this.history[audioId].layout; //pull the layout of this audio
      this.lanes = JSON.parse(JSON.stringify(layoutVersion));
    },

    slotPrep(audioId) {
      let history_slots = this.history[audioId].clipboard; //pull the original selected songs
      let current_slots = this.$refs.clipboard.slots;
      for (let i = 0; i < current_slots.length; i++) {
        // console.log(`Now check slot ${i}`);
        //if the songs are the same, skip
        let history_slot = history_slots[i];
        let current_slot = current_slots[i];
        let current_slot_ref_name = "selectedSongs" + i;
        // console.log(this.$refs.clipboard.$refs[current_slot_ref_name]);
        let current_slot_ref =
          this.$refs.clipboard.$refs[current_slot_ref_name][0];
        // console.log("current_slot_ref:", current_slot_ref);
        // let history_slot_item =
        //   history_slot.item[Object.keys(history_slot.item)[0]];

        if (!current_slot.item || Object.keys(current_slot.item) == 0) {
          // console.log("nothing in this slot!");
          // console.log(current_slot.item);
          if (!history_slot.item || Object.keys(history_slot.item) == 0) {
            console.log("nothing in both history and current slot!");
            continue;
          }
          let buffer_item = JSON.parse(JSON.stringify(history_slot.item));
          current_slot_ref.changeItem(buffer_item);
        } else if (!history_slot.item || Object.keys(history_slot.item) == 0) {
          console.log(
            "nothing in history slot, but something's in current slot"
          );
          let current_slot_item =
            current_slot.item[Object.keys(current_slot.item)[0]];
          let buffer_item = JSON.parse(JSON.stringify(current_slot_item));
          current_slot_ref.confirmDel(buffer_item);
        } else if (
          Object.keys(history_slot.item)[0] == Object.keys(current_slot.item)[0]
        ) {
          console.log("the same stuff in this slot!");
        } else {
          console.log("different songs, ready to change...");
          let current_slot_item =
            current_slot.item[Object.keys(current_slot.item)[0]];
          //delete the current one, just like click the delete button in selectedSongs.vue
          let buffer_item_current = JSON.parse(
            JSON.stringify(current_slot_item)
          );
          let buffer_item_history = JSON.parse(
            JSON.stringify(history_slot.item)
          );
          current_slot_ref.confirmDel(buffer_item_current); // when delete song, the data format doesn't include songId as the key, only content {artistName: ..., class: ...,}
          current_slot_ref.changeItem(buffer_item_history); //when add song, the data format is {0nbXyq5TXYPCO7pr3N8S4I: {…}}
        }
      }
    },
    playAudio() {
      if (this.currentPlayingAudio === null) {
        print("nothing is playing");
        return;
      }
      let audio = document.getElementById(this.currentPlayingAudio.id);
      audio.play();
      this.$refs.outputAudio.isPlaying = true;
    },
    pauseAudio() {
      // console.log("pause");
      let audio = document.getElementById(this.currentPlayingAudio.id);
      audio.pause();
      this.$refs.outputAudio.isPlaying = false;
    },
    deleteHistory(item) {
      let id = item.audioId;
      delete this.history[id];
    },
    getTimeStamp() {
      let currentDate = new Date();
      let currentDayOfMonth = currentDate.getDate();
      let currentMonth = currentDate.getMonth(); // Be careful! January is 0, not 1
      let currentYear = currentDate.getFullYear();

      let dateString =
        currentDayOfMonth + "-" + (currentMonth + 1) + "-" + currentYear;
      let currentTime =
        currentDate.getHours() +
        ":" +
        currentDate.getMinutes() +
        ":" +
        currentDate.getSeconds();
      let timeStamp = dateString + " " + currentTime;
      return timeStamp;
    },
    async getTaskStatus(taskID, baseUri) {
      let taskStatusURI = baseUri + "/requestStatus/" + taskID;

      let res = await axios
        .get(taskStatusURI)
        .then(function (response) {
          // console.log(response);
          return response.data;
        })
        .catch((err) => {
          this.genMsg =
            "Oops, something went wrong, please refresh the page ...";
          console.error(err);
        });
      console.log(res);
      return res;
    },
    async fetchResult(taskID, baseUri) {
      let fetchURI = baseUri + "/requestResult/" + taskID;
      console.log(fetchURI);
      let res = await axios
        .get(fetchURI, null)
        .then(function (response) {
          console.log("response data:", response.data);
          return response.data.task_result;
        })
        .catch((err) => {
          this.genMsg =
            "Oops, something went wrong, please refresh the page ...";
          console.error(err);
        });

      return res;
    },
    pause(milliseconds) {
      let dt = new Date();
      while (new Date() - dt <= milliseconds) {
        /* Do nothing */
      }
    },
    getSize() {
      this.containerWidth = document.getElementById("container").offsetWidth;
      this.containerHeight = document.getElementById("container").offsetHeight;
    },
  },
  mounted() {
    //get mixboard's size
    this.getSize();
    document.addEventListener("mousemove", (event) => {
      mousePosition.x = event.clientX;
      mousePosition.y = event.clientY;
    });
    document.addEventListener(
      "dragover",
      function (e) {
        mouseXY.x = e.clientX;
        mouseXY.y = e.clientY;
      },
      false
    );

    //pick a color palatte
    let random_index = Math.floor(Math.random() * this.color_palatte.length);
    let color_theme = this.color_palatte[random_index];
    this.color_theme = color_theme;
    //assign the color theme to four slots and the playing blocks
    let slots = this.$refs.clipboard.slots;
    var r = document.querySelector(":root");
    for (let i = 0; i < slots.length; i++) {
      let slot = slots[i];
      slot.color = color_theme.slots[i]; //notify clipboard.vue our chosen color
      this.$refs.clipboard.$refs[slot.ref][0].color = color_theme.slots[i]; //notify SelectedSongs.vue our chosen color for this slot
      r.style.setProperty(`--slot${i}`, color_theme.slots[i]); //assign colors to layout blocks, blocks' colors are controlled by <style>
      this.$refs.clipboard.$refs[slot.ref][0].slotPosition = i; //assign slot position
    }
  },
};
</script>

<style scoped>
#container {
  height: max-content;
  width: 100%;
  position: relative;
}

#fourLanes {
  width: 100%;
  height: 100%;
  position: relative;
  top: 0;
  left: 0;
}

.albumCover {
  margin-bottom: 2px;
  margin-right: 2px;
  padding-right: 2px;
  padding-bottom: 2px;
}

.grid-item-song0 {
  background: var(--slot0) !important;
  opacity: 1;
  transform: translate3d(10px, 10px, 0px);
  overflow: hidden;
}

.grid-item-song1 {
  background: var(--slot1) !important;
  opacity: 0.9;
  transform: translate3d(10px, 10px, 0px);
  overflow: hidden;
}

.grid-item-song2 {
  background: var(--slot2) !important;
  opacity: 0.9;
  transform: translate3d(10px, 10px, 0px);
  overflow: hidden;
}

.grid-item-song3 {
  background: var(--slot3) !important;
  opacity: 0.9;
  transform: translate3d(10px, 10px, 0px);
  overflow: hidden;
}

.remove {
  position: absolute;
  right: 2px;
  top: 0;
  cursor: pointer;
}

/* Hide scrollbar for Chrome, Safari and Opera */
.scrollbar-hidden::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge add Firefox */
.scrollbar-hidden {
  -ms-overflow-style: none;
  scrollbar-width: none;
  /* Firefox */
}

.vue-grid-layout {
  background: #eee;
  max-height: 130px;
}

.grid-layout-content {
  position: absolute;
  top: 50%;
  margin-top: -30px;
  left: 40%;
  margin-left: -30px;
}

/* 
.vue-grid-item:not(.vue-grid-placeholder) {
  background: rgb(194, 193, 143);
  border: 1px solid black;
  touch-action: none;
  z-index: 9;
} */

.vue-grid-item .resizing {
  opacity: 0.7;
}

.vue-grid-item.vue-grid-placeholder {
  background: green !important;
}

.grid-widget {
  background: #a3bce2;
  opacity: 0.7;
  border: 1px solid rgb(80, 80, 80);
  margin: 0px;
  height: 200px !important;
  z-index: 1;
}

.grid-widget {
  height: 180px !important;
}

.grid-item-content {
  height: 100%;
  padding-bottom: 1%;
  overflow: hidden;
  display: grid;
  grid-template-columns: repeat(auto-fill, 100px);
  grid-gap: 5px;
  box-sizing: border-box;
}

.activeBlock {
  background: yellow !important;
  opacity: 1;
  animation: 1s infinite alternate ease-out breathing-color--dark !important;
  animation-duration: 1s;
}

@keyframes breathing-color--dark {
  from {
    background-color: yellow;
  }

  to {
    background-color: #05fec2;
  }
}

.text {
  font-size: 0.7vw;
}

.songname {
  max-height: 15%;
  margin: 2%;
  overflow: hidden;
}

.generateButton {
  text-align: center;
}

.v-btn {
  min-width: 36px;
}

h1 {
  font-size: 5rem;
  font-weight: 900;
  line-height: 1.1;
  max-inline-size: 15ch;
  color: #4a63a1;
}

body {
  min-block-size: 100%;
  font-family: "Fugaz One", cursive;

  display: grid;
  place-content: center;
  padding: 5vmin;
}

#text-container {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  height: 100%;
  width: 100%;
  padding-left: 3rem;
  margin-right: 0px;
}

.laneName {
  writing-mode: vertical-rl;
  transform: rotate(-180deg);
  text-transform: uppercase;
  font-family: "Fantasy";
  font-size: 2.5vh;
  display: block;
  /* text-align: right; */
  margin-right: 0px;
  /* Safari */
  -webkit-transform: rotate(-180deg);

  /* Firefox */
  -moz-transform: rotate(-180deg);

  /* IE */
  -ms-transform: rotate(-180deg);

  /* Opera */
  -o-transform: rotate(-180deg);
}

.noselect {
  -webkit-touch-callout: none;
  /* iOS Safari */
  -webkit-user-select: none;
  /* Safari */
  -khtml-user-select: none;
  /* Konqueror HTML */
  -moz-user-select: none;
  /* Old versions of Firefox */
  -ms-user-select: none;
  /* Internet Explorer/Edge */
  user-select: none;
  /* Non-prefixed version, currently
                                   supported by Chrome, Edge, Opera and Firefox */
}
</style>
