<template>
  <v-layout>
    <mix-board ref="mixboard"></mix-board>
  </v-layout>
</template>

<script>
import MixBoard from "../components/MixBoard";

export default {
  // eslint-disable-next-line
  name: "Home",
  components: {
    MixBoard,
  },
};
</script>
