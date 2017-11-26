<template>
  <div id="app">
    <div class="container">
      <div class="row">
        <div class="col-md-offset-2 col-md-8">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'app'
};
</script>
