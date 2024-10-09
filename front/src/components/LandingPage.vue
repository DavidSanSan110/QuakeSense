<template>
  <div class="disclaimer">
    <img src="/Empresa.jpg" alt="Empresa" class="disclaimer-image" />
    <button @click="navigateToMarsModel" class="continue-button">START</button>
  </div>
</template>

<script>
export default {
  methods: {
    navigateToMarsModel() {
      this.$router.push({ name: "MarsModel" });
    },
  },
};
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&display=swap");

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body,
html {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}

.disclaimer {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.disclaimer-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
}

.continue-button {
  position: absolute;
  top: 54%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 15px 30px;
  font-size: 28px;
  font-family: "Montserrat", sans-serif;
  font-weight: 600;
  background: linear-gradient(135deg, #1b2735, #090a0f);
  color: #fff;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  text-transform: uppercase;
  letter-spacing: 2px;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.continue-button:hover {
  background: linear-gradient(135deg, #2c3e50, #1c1f26);
  box-shadow: 0 0 30px rgba(255, 255, 255, 0.7);
}
</style>
