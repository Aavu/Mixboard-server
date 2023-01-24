var PlayLine = function playLine(canvas, height, width = 5, fullScreenSecond) {
  let playLine = {
    canvas: canvas,
    width: width,
    height: height,
    color: "#a3bce2",
    positionX: 0,
    fullScreenSecond: fullScreenSecond,
    draw: function (currentPlaybackTime) {
      let context = this.canvas.getContext("2d");
      let fullScreenSecond = this.fullScreenSecond;
      // let fullScreenWidth = this.canvas.width;
      let currentPlayPos = (currentPlaybackTime / fullScreenSecond) * width;
      // console.log(
      //   "currentPlayPos",
      //   currentPlaybackTime,
      //   fullScreenSecond,
      //   fullScreenWidth,
      //   currentPlayPos
      // );
      context.beginPath();
      context.fillStyle = this.color;
      context.globalAlpha = 1;
      context.fillRect(currentPlayPos, 0, 2, this.height);
      this.positionX = currentPlayPos;
    },
  };
  return playLine;
};

export { PlayLine };
