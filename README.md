[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/7tomars/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/7tomars/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# News Image — Friday 20 November 2026

One newspaper-poster image that sums up the world news of Friday 20 November 2026: Russia's massive overnight air attack on Ukraine; Cyclone Akvan's landfall in Odisha; a tanker on fire in the Strait of Hormuz; Saudi Arabia intercepting a Houthi missile a day after the PIF Tower was hit; the EU–UK post-Brexit summit in Brussels; the Kerch Bridge rail link reopening; global stocks sliding as the AI sell-off deepens; and the EU mobilising another EUR 1 billion in military aid for Ukraine.

## How to run

Requires Python 3.12+ and nothing else — standard library only, no network, no external fonts or image libraries. The program defines its own 5×7 bitmap font and its own PNG encoder.

```sh
python3 main.py
```

This writes `entry.png` (1024×1024, under 1 MiB) into `$MAKEFUN_OUTPUT_DIR` when that variable is set, otherwise into `/output`. Runs are deterministic: two runs produce byte-identical output.

## Date discipline

Every story on the poster was verified against sources actually published on Friday 20 November 2026. These date traps were checked and kept out of the poster:

- Kenya's last Ebola patient actually went home 11 November, not 20 November.
- The US Senate energy-permitting bill passed on Thursday evening 19 November.
- The Pete Rose pardon was announced Thursday 19 November.
- Bukele registered Thursday 19 November.
- The Senegal migrant boat capsized Wednesday 18 November.
- The Sudan gold-mine drone strike was Wednesday 18 November.
- The IAEA Yongbyon report was 18–19 November.
- The US–Venezuela military deal was signed Wednesday 18 November.
- The Gaza Yellow Line incursion was 18–19 November.
- The White House cyber director was fired Thursday night 19 November.

## Sources

Each story was verified in at least two outlets published on 20 November 2026:

1. Russia's air attack on Ukraine — CNN / Reuters / Military.com
2. Cyclone Akvan in Odisha — IMD / The Hindu BusinessLine / Sambad English
3. Tanker fire in the Strait of Hormuz — Reuters / MarineLink
4. Saudi interception and Hodeidah strike — AP / Digital Dhaka News / US News Pulse
5. EU–UK summit in Brussels — AP / Consilium / European Commission Audiovisual Service
6. Kerch Bridge rail resumption — sagire.online / semblen.com / Kyiv Post
7. Global stocks slide — Reuters / The Hindu BusinessLine
8. EU military aid for Ukraine — Consilium / Agence Europe

## License

MIT — see [LICENSE](LICENSE).
