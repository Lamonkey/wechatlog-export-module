<script setup lang="ts">
import ContactsList from '@/components/messages/ContactsList.vue';
import ChatRecords from '@/components/messages/ChatRecords.vue';
import IsAutoShow from '@/components/messages/IsAutoShow.vue';
import {ref} from "vue";
import HomeView from "@/views/HomeView.vue";
import http from '@/router/axios.js';

const is_init = ref(false);
const init = (child_init: boolean) => {
  is_init.value = child_init;
}


const wxid = ref('');
const handleChildData = (val: any) => {
  wxid.value = val;
}

</script>
<template>
  <div id="chat_view" class="common-layout">
    <div v-if="!is_init">
      <IsAutoShow @isAutoShow="init"/>
    </div>
    <div v-else>
      <el-container>
        <!--  这是左边的list    -->
        <el-aside width="auto" style="overflow-y: auto; height: calc(100vh);">
          <ContactsList @wxid="handleChildData"/>
        </el-aside>
        <!-- END 这是左边的list -->

        <!--这是右边的具体聊天记录-->
        <div v-if="wxid != ''" style="height: calc(100vh);width: 100%;">
          <ChatRecords :wxid="wxid"/>
        </div>

        <div v-else style="width: 100%;height: 100%">
          <HomeView/>
        </div>
        <!-- END 这是右边的具体聊天记录 -->
      </el-container>

    </div>
  </div>
</template>

<style scoped>

</style>