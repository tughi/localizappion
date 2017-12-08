<template>
  <div>
    <template v-if="string.suggestions.length">
      <p>Already submitted suggestion{{ string.suggestions.length > 1 ? "s" : "" }}:</p>
      <div class="list-group">
        <button v-for="(suggestion, index) in string.suggestions" :key="index" :class="['suggestion', 'list-group-item', suggestionValue === suggestion.value ? 'active' : '', disabled ? 'disabled' : '']" :disabled="disabled" @click="selectSuggestion(index)">
            <span :class="['glyphicon', suggestionValue === suggestion.value ? 'glyphicon-check' : 'glyphicon-unchecked']"></span>{{ suggestion.value }}
        </button>
        <button :class="['suggestion', 'list-group-item', newSuggestion ? 'active' : '', disabled ? 'disabled' : '']" :disabled="disabled" @click="selectSuggestion(-1)">
          <span :class="['state-icon', 'glyphicon', newSuggestion ? 'glyphicon-check' : 'glyphicon-unchecked']"></span><strong>I have a better suggestion...</strong>
        </button>
      </div>
    </template>

    <div v-if="newSuggestion">
      <p>My suggestion:</p>
      <div class="form-group">
        <input v-model.trim="suggestionValue" type="text" class="form-control" placeholder="Suggestion" :disabled="disabled">
      </div>
    </div>

    <div class="form-group">
      <button @click="skipString" class="btn btn-default" :disabled="disabled">Skip</button>
      <span v-if="disabled" class="btn btn-primary disabled pull-right busy">
        <span class="text">Submit</span>
        <span class="spinner">
          <span class="rect1"></span>
          <span class="rect2"></span>
          <span class="rect3"></span>
          <span class="rect4"></span>
          <span class="rect5"></span>
        </span>
      </span>
      <button v-else class="btn btn-primary pull-right" :disabled="!isSuggestionValid()" @click="submit()">Submit</button>
    </div>
  </div>
</template>

<script>
import '../../node_modules/spinkit/css/spinkit.css';

export default {
  name: 'String',

  props: [
    'language',
    'skipString',
    'string'
  ],

  data() {
    var newSuggestion = false;
    var suggestionValue = '';
    if (this.string.suggestions.length === 0) {
      newSuggestion = true;
    } else {
      var votedSuggestion = this.string.suggestions.find(suggestion => 'voted' in suggestion);
      if (votedSuggestion) {
        suggestionValue = votedSuggestion.value;
      }
    }

    return {
      disabled: false,
      newSuggestion: newSuggestion,
      suggestionValue: suggestionValue
    };
  },

  methods: {
    selectSuggestion(index) {
      this.newSuggestion = index < 0;
      this.suggestionValue = index < 0 ? '' : this.string.suggestions[index].value;
    },

    isSuggestionValid() {
      return this.suggestionValue.length > 0;
    },

    submit() {
      this.disabled = true;

      this.$emit('submit-suggestion', {
        string: this.string.name,
        plural_form: 'other',
        value: this.suggestionValue
      });
    }
  }
};
</script>

<style scoped>
.suggestion {
  padding-left: 3em;
}
.suggestion:focus {
  outline: none;
}
.suggestion > .glyphicon {
  position: absolute;
  left: 1em;
  top: 12px;
}

.spinner {
  display: block;
  width: 50px;
  height: 1em;
  text-align: center;
}

.spinner > span {
  background-color: #fff;
  height: 100%;
  width: 2px;
  display: inline-block;
  
  -webkit-animation: sk-stretchdelay 1.2s infinite ease-in-out;
  animation: sk-stretchdelay 1.2s infinite ease-in-out;
}

.spinner .rect2 {
  -webkit-animation-delay: -1.1s;
  animation-delay: -1.1s;
}

.spinner .rect3 {
  -webkit-animation-delay: -1.0s;
  animation-delay: -1.0s;
}

.spinner .rect4 {
  -webkit-animation-delay: -0.9s;
  animation-delay: -0.9s;
}

.spinner .rect5 {
  -webkit-animation-delay: -0.8s;
  animation-delay: -0.8s;
}

@-webkit-keyframes sk-stretchdelay {
  0%, 40%, 100% { -webkit-transform: scaleY(0.4) }  
  20% { -webkit-transform: scaleY(1.0) }
}

@keyframes sk-stretchdelay {
  0%, 40%, 100% { 
    transform: scaleY(0.4);
    -webkit-transform: scaleY(0.4);
  }  20% { 
    transform: scaleY(1.0);
    -webkit-transform: scaleY(1.0);
  }
}

.btn.busy {
  position: relative;
}

.btn.busy > .text {
  visibility: hidden;
}

.btn.busy > .spinner {
  position: absolute;
  top: 50%;
  margin-top: -0.5em;
  left: 50%;
  margin-left: -25px;
}
</style>
