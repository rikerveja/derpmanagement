// src/store.js
import { createStore } from 'vuex';

export default createStore({
  state: {
    user: {
      username: '',
      email: ''
    }
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
    }
  }
});