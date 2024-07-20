<script>
import axios from 'axios'

export default {

    props: {
        showText: Boolean
    },
   
    methods: {
        incrementLikes() {
            axios.post('http://localhost:8000/feedback?feedback=1')
        },
        decrementLikes() {
            axios.post('http://localhost:8000/feedback?feedback=0')
        }
    }
}
</script>

<template>
    <div v-show="showText">
         Was this response good or bad?
        <span class="right">
            <img @click="incrementLikes" class="image like" src="../assets/like.png" alt="Like">  Like 
            <img @click="decrementLikes" class="image dislike" src="../assets/dislike.png" alt="Dislike">  Dislike
        </span>
    </div>
</template>

<style>
    .image {
        padding-top: 10px;
        height: 40px;
    }
    .dislike {
        padding-left: 25px;
    }
    .right {
        margin-left: 40px;
    }
    .like {
        margin-bottom: 15px;
    }
</style>