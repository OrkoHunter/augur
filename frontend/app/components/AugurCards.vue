<template>
  <div>

    <!-- content to show if app has no state yet -->
    <div :class="{ hidden: hasState }">
      <section class="unmaterialized">
        <h3>Enter a GitHub URL to get started</h3>
        <input type="text" class="search reposearch" placeholder="GitHub URL" @change="onRepo"/>
      </section>
      <section class="unmaterialized">
        <h3>Downloaded Git repositories</h3>
        <div v-for="repo in downloadedRepos">
          <a :href="'?git=' + btoa(repo.url)" class="repolink">{{ repo.url }}</a> (updated: {{ repo.updated }})
        </div>
      </section>
    </div>

    <!-- content to show if app does have a repo to show -->
    <div :class="{ hidden: !hasState }">
      <nav class="tabs">
        <ul>
          <li :class="{ active: (currentTab == 'gmd'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="gmd">Growth, Maturity, and Decline</a></li>
          <li :class="{ active: (currentTab == 'diversityInclusion'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="diversityInclusion">Diversity and Inclusion</a></li>
          <li :class="{ active: (currentTab == 'risk'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="risk">Risk</a></li>
          <li :class="{ active: (currentTab == 'value'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="value">Value</a></li>
          <li :class="{ active: (currentTab == 'activity'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="activity">Activity</a></li>
          <li :class="{ active: (currentTab == 'experimental'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="experimental">Experimental</a></li>
          <li :class="{ active: (currentTab == 'git'), hidden: !gitRepo }"><a href="#" @click="changeTab" data-value="git">Git</a></li>
        </ul>
      </nav>  

      <div ref="cards">
        <div v-if="(baseRepo && (currentTab == 'gmd'))">
          <growth-maturity-decline-card></growth-maturity-decline-card>
        </div>
        <div v-if="(baseRepo && (currentTab == 'diversityInclusion'))">
          <diversity-inclusion-card></diversity-inclusion-card>
        </div>
        <div v-if="(baseRepo && (currentTab == 'risk'))">
          <risk-card></risk-card>
        </div>
        <div v-if="(baseRepo && (currentTab == 'value'))">
          <value-card></value-card>
        </div>
        <div v-if="(baseRepo && (currentTab == 'activity'))" id="activity">
          <base-repo-activity-card></base-repo-activity-card>
          <base-repo-ecosystem-card></base-repo-ecosystem-card>
          <div id="comparisonCards" v-bind:class="{ hidden: !comparedRepos.length }" v-for="repo in comparedRepos">
            <compared-repo-activity-card :comparedTo="repo"></compared-repo-activity-card>
          </div>
        </div>
        <div v-if="(baseRepo && (currentTab == 'experimental'))">
          <experimental-card></experimental-card>
        </div>
        <div v-if="(gitRepo && (currentTab == 'git'))">
          <git-card></git-card>
        </div>
        <section class="unmaterialized" v-if="(baseRepo && (currentTab == 'activity'))">
          <h3>Compare repository</h3>
          <input type="text" class="search reposearch" placeholder="GitHub URL" @change="onCompare"/>
        </section>
        <main-controls></main-controls>
      </div>
    </div>
  </div>
</template>

<script>
import MainControls from './MainControls'
import BaseRepoActivityCard from './BaseRepoActivityCard'
import BaseRepoEcosystemCard from './BaseRepoEcosystemCard'
import ComparedRepoActivityCard from './ComparedRepoActivityCard'
import GrowthMaturityDeclineCard from './GrowthMaturityDeclineCard'
import RiskCard from './RiskCard'
import ValueCard from './ValueCard'
import DiversityInclusionCard from './DiversityInclusionCard'
import GitCard from './GitCard'
import ExperimentalCard from './ExperimentalCard'

module.exports = {
  components: {
    MainControls,
    BaseRepoActivityCard,
    BaseRepoEcosystemCard,
    ComparedRepoActivityCard,
    GrowthMaturityDeclineCard,
    RiskCard,
    ValueCard,
    DiversityInclusionCard,
    GitCard,
    ExperimentalCard
  },
  data() {
    return {
      downloadedRepos: []
    }
  },
  computed: {
    hasState() {
      return this.$store.state.hasState
    },
    baseRepo() {
      return this.$store.state.baseRepo
    },
    gitRepo() {
      return this.$store.state.gitRepo
    },
    comparedRepos() {
      return this.$store.state.comparedRepos
    },
    currentTab() {
      return this.$store.state.tab
    }, 
  },
  methods: {
    onRepo (e) {
      this.$store.commit('setRepo', {
        githubURL: e.target.value
      })
    },
    onCompare (e) {
      this.$store.commit('addComparedRepo', {
        url: e.target.value
      })
    },
    changeTab (e) {
      this.$store.commit('setTab', {
        tab: e.target.dataset['value']
      })
      e.preventDefault();
    },
    getDownloadedRepos() {
      this.downloadedRepos = []
      window.AugurAPI.getDownloadedGitRepos().then((data) => {
        this.downloadedRepos = data
      })
    },
    btoa(s) {
      return window.btoa(s)
    }
  },
  mounted () {
    this.getDownloadedRepos()
  }
}
</script>