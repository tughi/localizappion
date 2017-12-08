<template>
  <div>
    <div class="form-group">
      <button @click="skipString" class="btn btn-default" type="button">Skip</button>
      <button class="btn btn-primary pull-right" :disabled="true" type="button">Submit</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Plurals',

  props: [
    'language',
    'skipString',
    'string'
  ]
};
</script>
