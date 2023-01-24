<template>
  <div>
    <!-- <v-btn text @click.stop="overlay = true" class="success"
      >Add new project</v-btn
    > -->
    <v-overlay
      v-model="overlay"
      :absolute="false"
      height="20px"
      width="20px"
      z-index="2"
    >
      <v-card>
        <v-card-title> Mashup Instructions </v-card-title>
        <v-card-text>
          <ul>
            <li>
              Click the + in the Song Selection window to select a song to
              incorporate in your mashup.
            </li>
            <li>
              Drag songs onto the different lanes and change the length to
              create your own mashup.
            </li>
            <li>
              The Dice buttons or Luckyme button will randomly select songs or
              randomly arrange a mashup layout for you.
            </li>
            <li>
              The Generate button will create the mashup, and then press play to
              listen.
            </li>
            <li>
              Click the History Library button next to the player to listen to
              your previously created mashups.
            </li>
          </ul>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" text @click.stop="overlay = false">
            CLOSE
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-overlay>
  </div>
</template>
<script>
export default {
  data() {
    return {
      overlay: false,
    };
  },
};
</script>
