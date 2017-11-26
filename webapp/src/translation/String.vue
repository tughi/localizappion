<template>
  <div>
    <p>How do you say the following in <strong>{{ language.name }}</strong>?</p>
    <ul class="list-group">
        <li class="string-value list-group-item">{{ string.value }}</li>
    </ul>
    
    <template v-if="string.suggestions.length">
      <p>Already submitted suggestion{{ string.suggestions.length > 1 ? "s" : "" }}:</p>
      <div class="list-group">
        <a v-for="(suggestion, index) in string.suggestions" :class="['suggestion', 'list-group-item', suggestionIndex === index ? 'active' : '']" :key="index" @click="suggestionIndex = index">
            <span :class="['glyphicon', suggestionIndex === index ? 'glyphicon-check' : 'glyphicon-unchecked']"></span>{{ suggestion.value }}
        </a>
        <a :class="['suggestion', 'list-group-item', suggestionIndex === -1 ? 'active' : '']" @click="suggestionIndex = -1">
          <span :class="['state-icon', 'glyphicon', suggestionIndex === -1 ? 'glyphicon-check' : 'glyphicon-unchecked']"></span><strong>I have a better suggestion...</strong>
        </a>
      </div>
    </template>

    <div v-if="suggestionIndex === -1">
      <p>My suggestion:</p>
      <div class="form-group">
        <input v-model.trim="suggestion" type="text" class="form-control" placeholder="Suggestion">
      </div>
    </div>

    <div class="form-group">
      <button @click="skipString" class="btn btn-default" type="button">Skip</button>
      <button class="btn btn-primary pull-right" :disabled="!isSuggestionValid()" type="button">Submit</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'String',

  props: [
    'language',
    'skipString',
    'string'
  ],

  watch: {
  },

  data() {
    return {
      suggestion: '',
      suggestionIndex: null
    };
  },

  methods: {
    isSuggestionValid() {
      return this.suggestion.length > 0;
    }
  }
};
</script>

<style scoped>
.suggestion {
  padding-left: 3em;
}
.suggestion > .glyphicon {
  position: absolute;
  left: 1em;
  top: 12px;
}
</style>
