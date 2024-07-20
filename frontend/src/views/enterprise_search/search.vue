<script setup>
import { Form, Field } from 'vee-validate';
import { ref } from 'vue';
import * as Yup from 'yup';
import axios from 'axios';
import LikeDislikeButtons from '../../components/LikeDislikeButtons.vue';
import GetStats from './GetStats.vue'

//import { useUsersStore, useAlertStore } from '@/stores';
import { router } from '@/router';

const showText = ref(false);

async function onSubmit(values) {
    if (values.document){
        console.log(">>>>>>>>>>>> "+values.document)
        const params = new URLSearchParams();
        params.append('query', values.document);
        axios.post('http://localhost:8000/ask?' + params.toString())
        .then(res => {
            if (res.status === false) {
                // Handle the error here...
                console.log(">>>>>>>>>>>> success");
            } else {
                // Handle the user data here...
                console.log(">>>>>>>> "+res.data.response);
                document.getElementById("answer").innerHTML = res.data.response;
                showText.value = true;
            }
        });
          /*
        .then(response => {
            console.log(">>>>>>>>>>>> URL posted for indexing successfully")
        })
        .catch(error => {
            console.log(">>>>>>>>>>>> URL posted for indexing successfully")
        });*/        
    }
}
</script>

<template>
    <div class="card m-3">
        <h4 class="card-header">ENTERPRISE AI SEARCH</h4>
        <div class="card-body">
            <Form @submit="onSubmit" :validation-schema="schema" v-slot="{isSubmitting }">
                <div class="form-group">
                    <label>Query</label>
                    <Field name="document" type="text" class="form-control" />
                    
                </div>
                <div class="form-group">
                    <label>OUTPUT</label>
                    <div id="answer" style="border: 1px solid #ddd;cborder-radius: 5px; padding: 20px 5px; background: black; color: #fff; font-size: 13px;">...</div>
                </div>
                <LikeDislikeButtons :showText="showText"/>
                <div class="form-group">
                    <button @click="changeValue" class="btn btn-primary" :disabled="isSubmitting">
                        <span v-show="isSubmitting" class="spinner-border spinner-border-sm mr-1"></span>
                        Generate Output
                    </button>
                    <router-link to="upload" class="btn btn-link">Cancel</router-link>
                </div>
            </Form>
            <GetStats :showText="showText"/>
        </div>
    </div>
</template>