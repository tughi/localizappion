<template>
  <div>
    <p>How do you say the following in <strong>{{ language.name }}</strong>?</p>
    <ul class="list-group">
        <li class="string-value list-group-item">{{ string.value }}</li>
    </ul>
    
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
