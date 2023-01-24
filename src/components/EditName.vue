<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <template v-slot:activator="{ on, attrs }">
      <v-btn
        color="grey lighten-1"
        v-bind="attrs"
        v-on="on"
        icon
        @click="getAudioName"
      >
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Rename Audio</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-text-field
            v-model="value"
            label="Rename Audio"
            required
          ></v-text-field>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="closeDialog"> Close </v-btn>
        <v-btn color="blue darken-1" text @click="saveEdit()"> Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data: () => ({
    dialog: false,
    value: "",
  }),
  methods: {
    test() {
      console.log(this.value);
    },
    saveEdit() {
      this.dialog = false;
      this.$emit("saveEdit", this.value);
      // change value back to empty
      // this.value = "";
    },
    getAudioName() {
      this.$emit("getAudioName");
    },
    closeDialog() {
      this.dialog = false;
    },
  },
};
</script>
