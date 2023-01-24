import Vue from "vue";
import Vuetify from "vuetify/lib/framework";
// import "vuetify/src/styles/main.sass";

Vue.use(Vuetify);

const vuetify = new Vuetify({
  theme: {
    themes: {
      light: {
        primary: "#A3BCE2",
        secondary: "#F5FCCA",
        third: "#F3B2E5",
        anchor: "#8c9eff",
      },
    },
  },
});
export default vuetify;
