{
  description = "Application packaged using poetry2nix";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.nixpkgs-matplotlib.url = "github:NixOS/nixpkgs/dbe80f4b2c007120eb8244883de8e3ea3140b7f1";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, nixpkgs-matplotlib, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        inherit (poetry2nix.legacyPackages.${system}) mkPoetryEnv defaultPoetryOverrides;
        pkgs = nixpkgs.legacyPackages.${system};
        overrides = defaultPoetryOverrides.extend (self: super: {
            open-python = super.open-python.overridePythonAttrs
            (
              old: {
                buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
              }
            );
            matplotlib = nixpkgs-matplotlib.legacyPackages.${system}.python311Packages.matplotlib;
            z3-solver = pkgs.python311Packages.z3;
          });
      in {
        devShells = {
          lay-it-out = (let poetryEnv = mkPoetryEnv {
            projectDir = ./.;
            python = pkgs.python311;
            preferWheels = true;
            inherit overrides;
          };
          in poetryEnv.env.overrideAttrs (super: {buildInputs = [ pkgs.graphviz pkgs.jq ];}));
          default = self.devShells.${system}.lay-it-out;
        };

      });
}
