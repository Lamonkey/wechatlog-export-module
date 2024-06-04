<script setup lang="ts">

import ChatEChartsIndex from "@/components/chatecharts/ChatEChartsIndex.vue";

</script>

<template>
  <div style="background-color: #d2d2fa; height: 100vh; display: grid; place-items: center; ">
    <!--    <h2 style="text-align: center">欢迎使用<a href="https://github.com/xaoyaoo/PyWxDump.git">PyWxDump</a>聊天记录查看工具!-->
    <!--    </h2>-->
    <!--    <h3 style="text-align: center">-->
    <!--      用于统计微信聊天记录，包括聊天记录数量、聊天记录总字数、聊天记录总图片数量<br>聊天记录总视频数量、聊天记录总文件数量、聊天记录总语音数量等等。-->
    <!--      行成统计报表，方便用户查看自己的聊天记录情况-->
    <!--    </h3>-->
    <ChatEChartsIndex/>
  </div>
</template>

<style scoped>

</style>