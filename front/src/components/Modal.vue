<!-- Modal.vue -->
<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content">
      <slot></slot> <!-- Esto permite pasar contenido al modal -->
      <button @click="close" class="close-button">Close</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Modal',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    close() {
      this.$emit('close'); // Emitimos un evento para cerrar el modal
    }
  }
}
</script>

<style>
/* Estilos para el Modal */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Montserrat', sans-serif;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  max-width: 70%;
  width: 100%;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  text-align: center;
  position: relative;
  margin: auto; 
}

.close-button {
  background: #f44336;
  color: white;
  border: none;
  font-family: 'Montserrat', sans-serif;
  font-size: 16px;
  cursor: pointer;
  margin-top: 20px;
  padding: 10px 20px;
  border-radius: 5px;
  transition: background 0.3s, transform 0.2s;
}

.close-button:hover {
  background: #d32f2f;
  transform: scale(1.05);
}

.close-button:focus {
  outline: none;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
}
</style>
