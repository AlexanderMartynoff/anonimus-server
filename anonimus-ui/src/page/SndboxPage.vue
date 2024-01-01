<template>
    <n-layout position="absolute">
      <n-layout-header style="height: 64px; padding: 24px" bordered>
        Yiheyuan Road
      </n-layout-header>
      <n-layout has-sider position="absolute" style="top: 64px; bottom: 64px">
        <n-layout-sider bordered content-style="padding: 24px;">
          Handian Bridge
        </n-layout-sider>
        <n-layout>
            <n-tabs type="line" animated>
                <n-tab-pane name="oasis" tab="Oasis">
                    Wonderwall
                </n-tab-pane>
                <n-tab-pane name="the beatles" tab="the Beatles">
                    Hey Jude
                </n-tab-pane>
                <n-tab-pane name="jay chou" tab="Jay Chou">
                    Qilixiang
                </n-tab-pane>
            </n-tabs>
        </n-layout>
      </n-layout>
      <n-layout-footer
        bordered
        position="absolute"
        style="height: 64px; padding: 24px"
      >
        城府路
      </n-layout-footer>
    </n-layout>
</template>