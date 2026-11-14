"""Start Blockwerk. --screenshot captures the first-run UI for build verification."""
import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Blockwerk Minecraft Java Launcher")
    parser.add_argument("--screenshot", metavar="PNG", help="Save a first-run UI screenshot and exit without network requests")
    parser.add_argument("--check-network", metavar="JSON", help="Check the Mojang catalog and write a diagnostic report without signing in")
    parser.add_argument("--check-auth", metavar="JSON", help="Report public launcher configuration without signing in or accessing an account")
    parser.add_argument("--check-updates",metavar="JSON",help="Check the configured launcher update feed without installing")
    parser.add_argument("--screenshot-page", choices=("play", "microsoft", "worlds", "versions", "skins", "updates", "servers"), default="play", help="Page for an optional UI screenshot")
    parser.add_argument("--check-platform", metavar="JSON", help="Write OS, architecture and runtime diagnostics without signing in")
    args = parser.parse_args()
    if args.check_platform:
        from blockwerk.platform_check import report
        Path(args.check_platform).write_text(json.dumps(report(), ensure_ascii=False, indent=2), encoding="utf-8")
        return 0
    if args.check_updates:
        from blockwerk.core import LauncherService,VERSION,human_error
        from blockwerk.updates import UpdateManager
        try:
            updater=UpdateManager(LauncherService().root)
            info=updater.check()
            report={'version':VERSION,'latest':info['version'],'newer':info['newer'],
                    'package_available':info['available'],'source_kind':info['source']['kind'],
                    'weekly_enabled':bool(updater.state.get('automatic',True)),'installed':False}
            code=0
        except Exception as error:
            report={'version':VERSION,'error':human_error(error),'installed':False};code=1
        Path(args.check_updates).write_text(json.dumps(report,indent=2),encoding='utf-8')
        return code
    if args.check_auth:
        from blockwerk.core import LauncherService, VERSION, REDIRECT_URI
        service = LauncherService()
        Path(args.check_auth).write_text(json.dumps({"version": VERSION,
            "client_id": service.settings.client_id or None,
            "client_id_configured": bool(service.settings.client_id),
            "minecraft_app_permission": "not_verified", "redirect_uri": REDIRECT_URI,
            "client_secret_required": False, "password_collected_by_launcher": False}, indent=2), encoding="utf-8")
        return 0
    if args.check_network:
        from blockwerk.core import LauncherService, VERSION, human_error, filter_versions
        try:
            versions, cached = LauncherService().list_versions()
            result = {"version": VERSION, "online": not cached, "catalog_count": len(versions), "cached": cached}
            result.update(releases=len(filter_versions(versions,"Vollversionen")), snapshots=len(filter_versions(versions,"Snapshots")))
        except Exception as error:
            result = {"version": VERSION, "online": False, "error": human_error(error)}
            # This diagnostic only requests the public Mojang version catalog;
            # no account or OAuth request is made and no credential is sent.
            context = error.__context__ or error
            result["network_error_type"] = type(context).__name__
            result["network_error_detail"] = str(context)
            import traceback
            result["network_traceback"] = "".join(traceback.format_exception(context))
        Path(args.check_network).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return 0 if result["online"] else 1
    if args.screenshot:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from blockwerk.ui import run
    return run(args.screenshot, {"play":0,"microsoft":6,"worlds":7,"versions":1,"skins":8,"updates":9,"servers":5}[args.screenshot_page])


if __name__ == "__main__":
    raise SystemExit(main())
