<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
import MarsModel from "./components/MarsModel.vue";
import LandingPage from "./components/LandingPage.vue";

export default {
  name: "App",
  components: {
    MarsModel,
    LandingPage,
  },
};
</script>
