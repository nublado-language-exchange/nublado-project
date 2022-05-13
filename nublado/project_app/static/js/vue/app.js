// Instantiate main app instance.
const app = Vue.createApp({
  data(){
    return {
      showSidebar: sidebarExpanded,
      sidebarOpenClass: 'sidebar-expanded',
      showNavbarMenu: false,
      navbarMenuOpenClass: 'is-active',
      windowWidth: 0,
      windowWidthSmall: 640,
      windowResizeTimer: null,
    }
  },
  computed: {
    smallWindow: function() {
      return this.windowWidth <= this.windowWidthSmall
    }
  },
  methods: {
    toggleSidebar(manual) {
      // If manual is set to true or false, override toggle.
      if (manual === true || manual === false) {
        this.showSidebar = manual
      } else {
        this.showSidebar = !this.showSidebar
      }
  
      if (this.showSidebar) {
        document.body.classList.add(this.sidebarOpenClass)
      } else {
        document.body.classList.remove(this.sidebarOpenClass)
      }
    },
    toggleNavbarMenu(manual) {
      // If manual is set to true or false, override toggle.
      if (manual === true || manual === false) {
        this.showNavbarMenu = manual
      } else {
        this.showNavbarMenu = !this.showNavbarMenu
      }
  
      if (this.showNavbarMenu) {
        this.$refs.navbarMenu.classList.add(this.navbarMenuOpenClass)
      } else {
        this.$refs.navbarMenu.classList.remove(this.navbarMenuOpenClass)
      }
    },
    windowResize() {
      // Fire event after window resize completes.
      clearTimeout(this.windowResizeTimer)
      this.windowResizeTimer = setTimeout(()=>{
        this.windowWidth = document.documentElement.clientWidth
        if (this.smallWindow) {
          console.log('small')
        } else {
        }
      }, 250);
    }
  },
  mounted() {
    this.$nextTick(function() {
      window.addEventListener('resize', this.windowResize)
      this.windowResize()
    })
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.windowResize)
  }
})

const vm = app.mount('#app-container')