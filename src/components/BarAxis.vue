<template>
  <canvas id="barAxis" ref="barAxis" :height="30" style="border: none"></canvas>
</template>

<script>
import { PlayLine } from "../js/playLine";

export default {
  props: {
    showBarAxis: { type: Boolean, required: false, default: true },
    barNumber: { type: Number, required: false, default: 12 },
    gridWeight: { type: Number, required: false, default: 1 },
    gridColor: { type: String, required: false, default: "#37403f" },
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
      let canvas = this.$refs.barAxis;
      let context = canvas.getContext("2d");
      let width = canvas.width;
      let height = canvas.height;
      context.clearRect(0, 0, width, height);
    },
    drawbarAxis() {
      let canvas = this.$refs.barAxis;
      let context = canvas.getContext("2d");
      let x = this.barNumber;
      let w = this.gridWeight;
      let c = this.gridColor;
      let width = canvas.width;
      let height = canvas.height;
      let x_scale = width / x;
      this.clear();
      for (let i = 0; i < x + 2; i++) {
        let x1 = x_scale * i;
        let y1 = 10;
        let x2 = x1;
        let y2 = height;
        context.beginPath();
        context.strokeStyle = c;
        context.lineWidth = w;
        context.moveTo(x1, y1);
        context.lineTo(x2, y2);
        context.stroke();
        if (i % 4 === 0) {
          context.font = "10px Comic Sans MS";
          context.fillStyle = "#37403f";
          context.fillText(i, x1 + 3, (y2 - y1 + 10) / 2);
        }
      }
      //add the bottom line
      let x1 = 0;
      let y1 = height;
      let x2 = width;
      let y2 = height;
      context.beginPath();
      context.strokeStyle = c;
      context.lineWidth = w;
      context.moveTo(x1, y1);
      context.lineTo(x2, y2);
      context.stroke();
    },

    fitToContainer(canvas) {
      // Make it visually fill the positioned parent
      canvas.style.width = "100%";
      //   canvas.style.height = "100%";
      // ...then set the internal size to match
      canvas.width = canvas.offsetWidth;
      //   canvas.height = canvas.offsetHeight;
    },

    refreshBarAxis(playbackTime, duration) {
      this.clear();
      this.drawbarAxis();
      this.drawPlayLine(playbackTime, duration);
    },

    drawPlayLine(playbackTime, duration) {
      let canvas = this.$refs.barAxis;
      let height = canvas.height;
      let fullScreenWidth = canvas.width;
      let playLine = PlayLine(canvas, height, fullScreenWidth, duration);
      playLine.draw(playbackTime);
    },
    //@click, check mouse x position, calculate the percentage, emit event
    getXPercent(event) {
      let canvas = this.$refs.barAxis;
      let rect = canvas.getBoundingClientRect();
      let x = event.clientX - rect.left;
      let canvasWidth = canvas.width;
      this.currentAudioLength = this.currentAudio.duration;
      //user click generate, MixBoard.vue send avg_tempo and the (audioLength/32bar_audioLength) to BarAxis.vue
      let totalWidth =
        canvasWidth * (this.currentAudioLength / this.fullScreenSecond);
      let percent = x / totalWidth;
      console.log("percent:", percent);
      if (percent < 1) {
        return percent;
      } else {
        return 1;
      }
    },
    //canvas add eventlistener
    addClickListener() {
      let canvas = this.$refs.barAxis;
      let that = this;
      canvas.addEventListener("mousedown", (event) => {
        let percent = that.getXPercent(event);
        that.$emit("getPercent", percent);
      });
    },
  },
  mounted() {
    // var canvas = document.querySelector("canvas");
    var canvas = document.getElementById("barAxis");
    this.fitToContainer(canvas);
    this.drawbarAxis();
    this.drawPlayLine(0, 100);
    this.addClickListener();
  },
};
</script>

<style></style>
