<template>
  <div v-if="translation">
    <div class="page-header">
      <h1>{{ translation.project.name }}</h1>
    </div>

    <String v-if="typeof string.value === 'string'" :key="stringIndex" :language="language" :skipString="skipString" :string="string" v-on:submit-suggestion="submit" />
    <Plurals v-else :key="stringIndex" :language="language" :skipString="skipString" :string="string" />
  </div>
</template>

<script>
import axios from 'axios';
import Plurals from '@/translation/Plurals';
import String from '@/translation/String';

export default {
  name: 'Translation',

  components: {
    Plurals,
    String
  },

  data() {
    return {
      translation: null,
      stringIndex: 0
    };
  },

  computed: {
    language() {
      return this.translation.language;
    },
    string() {
      return this.translation.strings[this.stringIndex];
    }
  },

  created() {
    axios
      .get(`/api/translators/${this.$route.params.translator}/translations/${this.$route.params.translation}`)
      .then(response => {
        this.translation = response.data;
        this.stringIndex = -1;
        this.skipString();
      });
  },

  methods: {
    skipString() {
      for (this.stringIndex++; this.stringIndex < this.translation.strings.length; this.stringIndex++) {
        var translatable = false;
        if (typeof this.string.value === 'string') {
          if (!this.string.suggestions.find(suggestion => 'voted' in suggestion)) {
            translatable = true;
          }
        } else {
          for (var pluralForm in this.string.suggestions) {
            if (!this.string.suggestions[pluralForm].find(suggestion => 'voted' in suggestion)) {
              translatable = true;
              break;
            }
          }
        }
        if (translatable) {
          break;
        }
        console.log('Skip: ' + this.string.name);
      }
    },

    submit(suggestion) {
      axios
        .post(`/api/translators/${this.$route.params.translator}/translations/${this.$route.params.translation}`, suggestion)
        .then(response => {
          this.translation = response.data;
          this.stringIndex--;
          this.skipString();
        });
    }
  }
};
</script>
