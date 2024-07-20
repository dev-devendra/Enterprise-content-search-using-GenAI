<script setup>
import { useAuthStore } from '@/stores';
import { router } from '@/router';

// redirect home if already logged in
const authStore = useAuthStore();
if (authStore.user) {
    router.push('/');
}
</script>

<template>
    <div class="container">
        <div class="row" style="display: flex; justify-content: center">
            <div class="col-sm-8">
                <router-view />
            </div>
        </div>
    </div>
</template>
