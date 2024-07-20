<script>
import axios from 'axios'
import { onUpdated } from 'vue';

export default {
    data() {
        return {
            cost: null,
            queries: null,
            liked: null,
            disliked: null
        }
    },

    props: {
        showText: Boolean
    },

    methods: {
        getStats() {
            axios.get('http://localhost:8000/stats')
            .then(res => {
                if (res.status === false) {
                    // Handle the error here...
                    console.log(">>>>>>>>>>>> error");
                } else {
                    // Handle the user data here...
                    this.cost = res.data.cost
                    this.queries = res.data.total_queries
                    this.liked = res.data.liked
                    this.disliked = res.data.disliked
                }
            });
        }
    },

   created() {
        this.getStats();
        setInterval(() => {
                this.getStats();
            }, 10000);
    }
}
</script>

<template>
    <div v-show="showText" class="main">
        <span class="stats_data"> Cost: ${{ cost }} </span>
        <span class="stats_data"> Queries: {{ queries }} </span>
        <span class="stats_data"> Liked: {{ liked }} </span>
        <span class="stats_data"> Disliked: {{ disliked }} </span>
    </div>
</template>

<style>
    .main{
        text-align: center;
        padding-top: 15px;
    }
    .stats_data {
        padding: 8px;
    }
</style>