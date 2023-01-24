<template>
  <v-app>
    <v-main>
      <v-app-bar app color="#7f91bc" dark height="50px">
        <span
          style="
            font-weight: bold !important;
            color: #f8f8ff;
            font-size: larger;
          "
          >Welcome to Mix Board</span
        >
        <v-spacer />
        <!--        <div id="nav">-->
        <!--          <router-link to="/">Home</router-link>-->
        <!--          |-->
        <!--          <router-link to="/about">About</router-link>-->
        <!--        </div>-->

        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon @click="popup">
              <v-icon v-bind="attrs" v-on="on">mdi-help</v-icon>
            </v-btn>
          </template>
          <span>Mashup Instructions</span>
        </v-tooltip>
      </v-app-bar>
      <router-view ref="view" class="mt-3"></router-view>
    </v-main>
  </v-app>
</template>

<script>
window._mfq = window._mfq || [];
(function () {
  var mf = document.createElement("script");
  mf.type = "text/javascript";
  mf.defer = true;
  mf.src =
    "//cdn.mouseflow.com/projects/73381aed-dc3a-4f09-a848-2128387dabf5.js";
  document.getElementsByTagName("head")[0].appendChild(mf);
})();

export default {
  name: "App",

  data: () => ({
    //
  }),
  methods: {
    popup() {
      this.$refs.view.$refs.mixboard.popup();
    },
  },
};
</script>

<style>
.vue-grid-item > .vue-resizable-handle {
  margin-right: 1px;
  width: 30px !important;
  height: 80% !important;
  cursor: col-resize !important;
  background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAmElEQVRIie2UMQqDMBRAtUsvIHYU6oGc6hHUq+nk2MX7KE4tLk6vyw9YMYJN4lDyxh/4LzxIgsDzK0CDnocNQQT0GsEI3GxIMlk4ASkQAk+ZtcYCkahUnQgS4O0qVSmz0mWq+5mpXv+f6nLQcd05mw/u+kYSDXLbQmbVIlFsKnD3HoB8p31tutyn0S5fplljNc0W5l+DR/EBicr3rNRw4+MAAAAASUVORK5CYII=)
    no-repeat fixed center !important;
}
</style>
