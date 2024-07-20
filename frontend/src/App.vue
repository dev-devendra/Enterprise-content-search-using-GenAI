<script setup>
import { useAuthStore } from '@/stores';

const authStore = useAuthStore();
</script>

<template>
    <div class="app-container" :class="authStore.user && 'bg-light'">
       <div style="display: flex; justify-content: start; width: 100%; padding: 20px 50px;">
        <img src="./assets/logo1.png" width="150" height="150" />
       </div>
        <div class="container pt-4 pb-4">
            <router-view />
        </div>
    </div>
</template>

<style>
@import '@/assets/base.css';
</style>