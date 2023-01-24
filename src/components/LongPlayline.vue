<template>
  <canvas
    id="largeCanvas"
    ref="largeCanvas"
    :height="canvasHeight"
    style="border: none"
  ></canvas>
</template>

<script>
import { PlayLine } from "../js/playLine";

export default {
  props: {
    canvasHeight: { type: Number, required: false, default: 300 },
    canvasWidth: { type: Number, required: false, default: 300 },
  },
  data() {
    return {
      currentAudio: null,
      currentAudioLength: null,
      fullScreenSecond: null,
    };
  },
  watch: {},
  methods: {
    clear() {
      // console.log("CLEAR!");
      let canvas = this.$refs.largeCanvas;
      let context = canvas.getContext("2d");
      let width = canvas.width;
      let height = canvas.height;
      context.clearRect(0, 0, width, height);
    },

    fitToContainer(canvas) {
      // Make it visually fill the positioned parent
      canvas.style.width = "100%";
      canvas.style.height = "100%";
      // ...then set the internal size to match
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    },

    refreshCanvas(playbackTime, duration) {
      this.clear();
      this.drawPlayLine(playbackTime, duration);
    },

    drawPlayLine(playbackTime, duration) {
      let canvas = document.getElementById("largeCanvas");
      let height = canvas.height;
      let fullScreenWidth = canvas.width;
      let playLine = PlayLine(canvas, height, fullScreenWidth, duration);
      console.log(height, fullScreenWidth, duration);
      playLine.draw(playbackTime);
    },
  },
  mounted() {
    var canvas = document.getElementById("largeCanvas");
    this.fitToContainer(canvas);
    this.drawPlayLine(0, 100);
  },
};
</script>

<style scoped>
#largeCanvas {
  z-index: 2;
  background-color: white;
  opacity: 0.2;
  pointer-events: none;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  height: 100%;
}
</style>
