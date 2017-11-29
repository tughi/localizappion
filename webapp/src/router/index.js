import Vue from 'vue';
import Router from 'vue-router';
import Translation from '@/translation/Translation';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/translators/:translator/translate/:translation',
      name: 'Translation',
      component: Translation
    }
  ]
});
