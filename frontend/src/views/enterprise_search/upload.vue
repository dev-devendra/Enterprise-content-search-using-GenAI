<script setup>
import { Form, Field } from 'vee-validate';
import * as Yup from 'yup';
import axios from 'axios';

//import { useAuthStore } from '@/stores';
/*
const schema = Yup.object().shape({
    username: Yup.string().required('Username is required'),
    password: Yup.string().required('Password is required')
});
*/
function sendFileAsFormData(file) {
  // Create a new FormData object
  var formData = new FormData();

  // Read the file content using FileReader
  var reader = new FileReader();
  reader.onload = function(event) {
    var fileContent = event.target.result;

    // Append the file and file content to the FormData object
    formData.append('file', file);
    formData.append('fileContent', fileContent);

    // Create the Fetch API request
    var request = new Request('http://localhost:8000/index_doc', {
      method: 'POST',
      body: formData,
      mode: 'no-cors'
    });

    // Send the request
    fetch(request)
      .then(function(response) {
        // Handle the response
        if (response.ok) {
          console.log('File uploaded successfully.');
          // Do something with the successful response
        } /*else {
          console.error('Error uploading file.');
          // Handle the error
        }*/
      })
      .catch(function(error) {
        console.error('Error:', error);
        // Handle the error
      });
  };

  // Read the file as text
  reader.readAsArrayBuffer(file);
}
async function onSubmit(values) {
    if (values.website){
        console.log(">>>>>>>>>>>> "+encodeURI(values.website));
        const params = new URLSearchParams();
        params.append('pageurl', values.website);
        axios.post('http://localhost:8000/index_webpage?' + params.toString())
        .then(response => {
            console.log(">>>>>>>>>>>> URL posted for indexing successfully")
        })
        .catch(error => {
        });        
    }else if(values.document){
        console.log(">>>>>>>>>>>> "+values.document[0].name);
        console.log(">>>>>>>>>>>> "+values.document[0].size);
        sendFileAsFormData(values.document[0]);
    }
    document.getElementById("infile").value = null;
    document.getElementById("site").value = null;

    /*
    var reader = new FileReader();
    reader.onload = function (event) {
        var data = event.target.result;
        console.log('Data: ' + data);
    };
    reader.readAsBinaryString(values.document[0]);    
    */
    /*
    const authStore = useAuthStore();
    const { username, password } = values;
    await authStore.login(username, password);
    */
}
</script>

<template>
    <div class="card m-3">
        <h4 class="card-header">UPLOAD DOCUMENT</h4>
        <div class="card-body">
            <Form @submit="onSubmit" :validation-schema="schema" id = "myForm" v-slot="{ isSubmitting }">
                <div class="form-group">
                    <label>Document</label>
                    <Field name="document" type="file" class="form-control" id="infile"/>
                    
                </div>
                <div class="form-group">
                    <label>Website</label>
                    <Field name="website" type="text" class="form-control"  id="site"/>

                </div>
                <div class="form-group">
                    <button class="btn btn-primary" :disabled="isSubmitting">
                        <span v-show="isSubmitting" class="spinner-border spinner-border-sm mr-1"></span>
                        Upload
                    </button> <p></p>
                    <router-link to="search" class="btn btn-primary">Search</router-link>
                </div>
            </Form>
        </div>
    </div>
</template>